import socket
import hashlib
import time
import logging


class MyHomeSocket:
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


class MyHomeLight():
    def __init__(self, where, gate: MyHomeSocket):
        self.where = str(where)
        self._gate = gate

    def turn_on(self):
        self._gate.turn_on_light(self.where)

    def turn_off(self):
        self._gate.turn_off_light(self.where)

    def is_on(self):
        return self._gate.is_light_on(self.where)


import logging

import voluptuous as vol

# Import the device class from the component that you want to support
from homeassistant.components.light import ATTR_BRIGHTNESS, Light, PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_PORT
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_USERNAME, default='admin'): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Awesome Light platform."""

    # Assign configuration variables. The configuration check takes care they are
    # present.
    host = config.get(CONF_HOST)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    # # Setup connection with devices/cloud
    hub = MyHomeSocket('192.168.1.13', 20000, 'azerty123')
    hub.connect()
    #
    # # Verify that passed in configuration works
    # if not hub.is_valid_login():
    #     _LOGGER.error("Could not connect to AwesomeLight hub")
    #     return False
    #
    # # Add devices
    add_devices(AwesomeLight(light) for light in hub.getLights())


class AwesomeLight(Light):
    """Representation of an Awesome Light."""

    def __init__(self, light: MyHomeLight):
        """Initialize an AwesomeLight."""
        self._light = light
        self._state = None

    @property
    def name(self):
        """Return the display name of this light."""
        return self._light.where

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._light.turn_on()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._light.turn_off()

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self._light.is_on()
