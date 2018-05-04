#!/usr/bin/env python
# coding: utf-8

import socket
import hashlib
import time
import logging


class MyHomeSocket:
    """Manage communication with myhomeserver1"""
    ENCODING = 'latin1'
    TIMEOUT = 1
    _socket = None

    def __init__(self, host, port, pwd):
        self.logger = logging.getLogger('myhome.MyHomeSocket')
        self.logger.debug('creating an instance of MyHomeSocket')
        self._host = host
        self._port = port
        self._pwd = pwd
        self.initSocket()

    def initSocket(self):
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.TIMEOUT)
        return self._socket

    def send(self, message):
        self.logger.debug("TX " + message)
        self._socket.send(message.encode(self.ENCODING))

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
