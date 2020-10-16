import logging
import unittest

from brownpaperbag.bpbgate import BpbGate


class BpbGateTestCase(unittest.TestCase):
    def setUp(self):
        self.my = BpbGate("192.168.1.**", 20000, "*******")

    def test_instance(self):
        self.assertIsInstance(self.my, BpbGate)

    def test_logger(self):
        self.assertIsInstance(self.my.logger, logging.getLoggerClass())
        log = logging.getLogger("NEW")
        self.my.logger = log
        self.assertEqual(self.my.logger, log)


if __name__ == "__main__":
    unittest.main()
