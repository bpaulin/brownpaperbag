#!/usr/bin/env python
# coding: utf-8

import socket
import hashlib
import time


class MyHomeSocket:
    def __init__(self, host, port, pwd):
        self._host = host
        self._port = port
        self._pwd = pwd
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, message):
        print("TX " + message)
        self._socket.send(message.encode('latin1'))

    def receive(self):
        message = self._socket.recv(4096)
        print("RX " + message.decode('latin1'))
        return message

    def connect(self):
        self._socket.connect((self._host, self._port))
        self.receive()
        self.send("*99*9##")
        self.receive()
        self.send("*#*1##")
        nonce = self.receive()
        ra = nonce[2:-2].decode('latin1')
        self.authent(ra)

    def _digit_to_hex(self, toconvert):
        return ''.join([hex(int(i))[2:] for i in [toconvert[i:i + 2] for i in range(0, len(toconvert), 2)]])

    def _hex_to_digit(self, toconvert):
        return ''.join([str(int(i, 16)).zfill(2) for i in toconvert])

    def authent(self, ra):
        print('Ra ' + ra)
        ra = self._digit_to_hex(ra)
        print('Ra ' + ra)
        rb = hashlib.sha256('rb'.encode('latin1')).hexdigest()
        print('Rb ' + rb)
        message = ra + rb + "736F70653E" + "636F70653E" + hashlib.sha256(self._pwd.encode('latin1')).hexdigest()
        print(message)
        message = hashlib.sha256(message.encode('latin1')).hexdigest()
        print(message)
        self.send("*#" + self._hex_to_digit(rb) + "*" + self._hex_to_digit(message) + "##")
        self.receive()
        # @todo check answer
        self.send("*#*1##")

    def sendcommand(self, who, what, where):
        self.send("*" + who + "*" + what + "*" + where + "##")

    def sendrawcommand(self, command):
        self.send(command)

my = MyHomeSocket("192.168.1.13", 20000, 'azerty123')
my.connect()
my.sendcommand('1', '1', '0012')
time.sleep(5)
my.sendcommand('1', '0', '0012')
lights = []
my.sendrawcommand('*#1*0##')
while True:
    response = my.receive().decode('latin1')
    if response == "*#*1##":
        break
    lights.append(response[5:-2])

print(lights)

# for light in lights:
#     print('light #'+light)
#     my.sendcommand('1','1',light)
#     time.sleep(5)
#     my.sendcommand('1','0',light)
# while response = my.receive().decode('latin1') != "*#*1##":
#     print('light')
