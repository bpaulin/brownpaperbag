import unittest
import myhome
from unittest.mock import patch


class MyHomeSocketTestCase(unittest.TestCase):
    def setUp(self):
        self.my = myhome.MyHomeSocket("192.168.1.13", 20000, 'azerty123')

    def test_something(self):
        self.assertIsInstance(self.my, myhome.MyHomeSocket)


if __name__ == '__main__':
    unittest.main()
