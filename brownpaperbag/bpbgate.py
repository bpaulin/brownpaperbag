import logging
import socket
import hashlib


class BpbGate:
    """Manage communication with myhomeserver1"""
    ENCODING = 'latin1'
    TIMEOUT = 5
    _socket = None

    def __init__(self, host, port, pwd):
        self.logger = logging.getLogger(__name__)
        self._host = host
        self._port = port
        self._pwd = pwd
        self.initSocket()

    def setlogger(self, logger):
        self.logger = logger

    def initSocket(self):
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.TIMEOUT)
        return self._socket

    def send(self, message):
        self.logger.debug("TX " + message)
        self._socket.sendall(message.encode(self.ENCODING))

    def receive(self):
        message = self._socket.recv(4096).decode(self.ENCODING)
        self.logger.debug("RX " + message)
        return message

    def connect(self):
        self.logger.debug("connection")
        try:
            self._socket.connect((self._host, self._port))
        except socket.timeout:
            self.logger.critical("connection timed out")
            return False
        self.receive()
        self.send("*99*9##")
        self.receive()
        self.send("*#*1##")
        nonce = self.receive()
        ra = nonce[2:-2]
        self.authent(ra)

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
        return ''.join([
            str(int(i, 16)).zfill(2)
            for i
            in toconvert
        ])

    def authent(self, ra):
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

    def sendcommand(self, who, what, where):
        self.send("*" + who + "*" + what + "*" + where + "##")

    def sendrequest(self, who, where):
        self.send("*#" + who + "*" + where + "##")
        state = self.receive()
        self.receive()
        return state

    def getLights(self):
        lights = []
        self.send('*#1*0##')
        while True:
            response = self.receive()
            if response == "*#*1##":
                break
            lights.append(MyHomeLight(response[5:-2], self))
        return lights

    def turn_on_light(self, where):
        try:
            self.sendcommand('1', '1', where)
        except BrokenPipeError:
            self.connect()
            self.sendcommand('1', '1', where)
        self.receive()

    def turn_off_light(self, where):
        try:
            self.sendcommand('1', '0', where)
        except BrokenPipeError:
            self.connect()
            self.sendcommand('1', '0', where)
        self.receive()

    def is_light_on(self, where):
        try:
            response = self.sendrequest('1', where)
        except BrokenPipeError:
            self.connect()
            response = self.sendrequest('1', where)
        return response[3] == '1'
