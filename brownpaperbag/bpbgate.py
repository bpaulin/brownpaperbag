import logging
import socket
import hashlib


class BpbGate:
    """Manage communication with myhomeserver1"""
    ENCODING = 'utf-8'
    TIMEOUT = 5
    _socket = None
    _logger = None

    def __init__(self, host, port, pwd):
        """Constructor"""
        self._host = host
        self._port = port
        self._pwd = pwd

    def set_logger(self, logger: logging.getLoggerClass()):
        """allow override of logger"""
        self._logger = logger

    def get_logger(self):
        """return logger, set it if needed"""
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    def set_socket(self, soc: socket.socket):
        """allow override of socket"""
        self._socket = soc

    def get_socket(self):
        """return socket, set it if needed"""
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.TIMEOUT)
        return self._socket

    def send(self, message):
        """send message to socket"""
        self._logger.debug("send: " + message)
        try:
            self.get_socket().sendall(message.encode(self.ENCODING))
        except BrokenPipeError:
            self._logger.debug("socket closed")
            self.connect()
            self._logger.debug("send: " + message)
            self.get_socket().sendall(message.encode(self.ENCODING))

    def receive(self):
        """read and return message to socket"""
        message = self.get_socket().recv(4096).decode(self.ENCODING)
        self._logger.debug("recv: " + message)
        return message

    def connect(self):
        """connect to socket and authent with hmac"""
        self._logger.info("connection")
        try:
            self.get_socket().connect((self._host, self._port))
        except socket.timeout:
            self._logger.critical("connection timed out")
            return False
        self.receive()
        self.send("*99*9##")
        self.receive()
        self.send("*#*1##")
        nonce = self.receive()
        ra = nonce[2:-2]
        ra = self._digit_to_hex(ra)
        # @todo random string
        rb = hashlib.sha256('rb'.encode(self.ENCODING)).hexdigest()
        message = ra + \
            rb + \
            "736F70653E" + \
            "636F70653E" + \
            hashlib.sha256(self._pwd.encode(self.ENCODING)).hexdigest()
        message = hashlib.sha256(message.encode(self.ENCODING)).hexdigest()
        self.send(
            "*#" +
            self._hex_to_digit(rb) +
            "*" +
            self._hex_to_digit(message) +
            "##"
        )
        self.receive()
        # @todo check answer
        self.send("*#*1##")

    @staticmethod
    def _digit_to_hex(string_of_digit):
        """Convert string of digits to string of hex"""
        return ''.join([
            hex(int(i))[2:]
            for i
            in [
                string_of_digit[i:i + 2]
                for i
                in range(0, len(string_of_digit), 2)
            ]
        ])

    @staticmethod
    def _hex_to_digit(toconvert):
        """convert string of hex to strings of digits"""
        return ''.join([
            str(int(i, 16)).zfill(2)
            for i
            in toconvert
        ])

    def send_command(self, who, what, where):
        """send who/what/where command"""
        self.send("*" + who + "*" + what + "*" + where + "##")

    def send_request(self, who, where):
        """send who/where request"""
        self.send("*#" + who + "*" + where + "##")
        state = self.receive()
        self.receive()
        return state

    def get_light_ids(self):
        """return list of all lights ids"""
        lights = []
        self.send('*#1*0##')
        while True:
            response = self.receive()
            if response == "*#*1##":
                break
            lights.append(response[5:-2])
        return lights

    def turn_on_light(self, where):
        """turn on light by id"""
        self.send_command('1', '1', where)
        self.receive()

    def turn_off_light(self, where):
        """turn off light by id"""
        self.send_command('1', '0', where)
        self.receive()

    def is_light_on(self, where):
        """request light state"""
        response = self.send_request('1', where)
        return response[3] == '1'

    def get_automation_ids(self):
        lights = []
        self.send('*#2*0##')
        while True:
            response = self.receive()
            if response == "*#*1##":
                break
            lights.append(response[5:-2])
        return lights

    def close_cover(self, where):
        self.send_command('2', '2', where)
        self.receive()

    def open_cover(self, where):
        self.send_command('2', '1', where)
        self.receive()

    def stop_cover(self, where):
        self.send_command('2', '0', where)
        self.receive()

    def is_cover_opening(self, where):
        response = self.send_request('2', where)
        return response[3] == '1'

    def is_cover_closing(self, where):
        response = self.send_request('2', where)
        return response[3] == '2'

    def is_cover_stopped(self, where):
        response = self.send_request('2', where)
        return response[3] == '0'
