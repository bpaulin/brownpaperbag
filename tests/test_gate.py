import unittest
import logging
import socket
from brownpaperbag.bpbgate import BpbGate


class BpbGateTestCase(unittest.TestCase):
    def setUp(self):
        self.my = BpbGate("192.168.1.**", 20000, '*******')

    def test_instance(self):
        self.assertIsInstance(self.my, BpbGate)

    def test_logger(self):
        self.assertIsInstance(self.my.logger, logging.getLoggerClass())
        log = logging.getLogger('NEW')
        self.my.logger = log
        self.assertEqual(self.my.logger, log)

    def test_my_home_soc(self):
        self.assertIsInstance(self.my.my_home_soc, socket.socket)
        soc = socket.socket()
        self.my.my_home_soc = soc
        self.assertEqual(self.my.my_home_soc, soc)


if __name__ == '__main__':
    unittest.main()
