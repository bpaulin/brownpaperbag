import unittest
from brownpaperbag.bpbgate import BpbGate


class BpbGateTestCase(unittest.TestCase):
    def setUp(self):
        self.my = BpbGate("192.168.1.**", 20000, '*******')

    def test_something(self):
        self.assertIsInstance(self.my, BpbGate)


if __name__ == '__main__':
    unittest.main()
