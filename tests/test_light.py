import unittest
from brownpaperbag.bpblight import BpbLight
from brownpaperbag.bpbgate import BpbGate


class BpbLightTestCase(unittest.TestCase):
    def setUp(self):
        self.my = BpbGate("192.168.1.**", 20000, '*******')
        self.light = BpbLight('11', self.my)

    def test_something(self):
        self.assertIsInstance(self.light, BpbLight)


if __name__ == '__main__':
    unittest.main()
