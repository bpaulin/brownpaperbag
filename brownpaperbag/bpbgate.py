import logging
import socket
import hashlib
from time import sleep

COVER_CLOSED = 0
COVER_OPENING = 1
COVER_CLOSING = 2


class BpbGate:
    """Manage communication with myhomeserver1"""
    ENCODING = 'utf-8'
    TIMEOUT = 3
    _socket = None
    _logger = None
    _light_ids = None
    _cover_ids = None

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
        self.get_logger().debug("send: " + message)
        try:
            self.get_socket().send(message.encode(self.ENCODING))
        except BrokenPipeError:
            self.get_logger().debug("socket closed")
            self.connect()
            self.get_logger().debug("send: " + message)
            self.get_socket().send(message.encode(self.ENCODING))

    def receive(self):
        """read and return message to socket"""
        message = self.get_socket().recv(4096).decode(self.ENCODING)
        self.get_logger().debug("recv: " + message)
        return message

    def connect(self):
        """connect to socket and authent with hmac"""
        self.get_logger().info("connection")
        try:
            self.get_socket().connect((self._host, self._port))
        except socket.timeout:
            self.get_logger().critical("connection timed out")
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
        try:
            self.receive()
        except socket.timeout:
            pass
        return state

    def get_ids(self, what):
        """return list of all 'what' ids"""
        items = []
        self.send('*#'+what+'*0##')
        while True:
            response = self.receive()
            if response == "*#*1##":
                break
            items.append(response[5:-2])
        uniq = []
        for item in items:
            if item not in uniq:
                uniq.append(item)
        return uniq

    def poll_devices(self):
        self.get_logger().info("polling lights")
        self._light_ids = self.get_ids('1')
        self.get_logger().info("polling cover")
        self._cover_ids = self.get_ids('2')

    def get_light_ids(self):
        """return list of all lights ids"""
        return self._light_ids

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
        self.get_logger().info("getting light state "+where)
        response = self.send_request('1', where)
        return response[3] == '1'

    def get_cover_ids(self):
        """return all covers id"""
        return self._cover_ids

    def close_cover(self, where):
        """close cover by id"""
        self.get_logger().info("closing cover "+where)
        self.send_command('2', '2', where)
        sleep(0.2)
        self.receive()

    def open_cover(self, where):
        """open cover by id"""
        self.get_logger().info("opening cover "+where)
        self.send_command('2', '1', where)
        sleep(0.2)
        self.receive()

    def stop_cover(self, where):
        """stop cover by id"""
        self.get_logger().info("stopping cover "+where)
        self.send_command('2', '0', where)
        sleep(0.2)
        self.receive()

    def get_cover_state(self, where):
        """ return cover state"""
        response = self.send_request('2', where)
        return response[3]
