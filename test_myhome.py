import unittest
import myhome
from unittest.mock import patch


class MyHomeSocketTestCase(unittest.TestCase):
    def setUp(self):
        self.my = myhome.MyHomeSocket("192.168.1.13", 20000, 'azerty123')

    def test_something(self):
        self.assertIsInstance(self.my, myhome.MyHomeSocket)

    # 3rd way uses function defined inside test class but before patch decorator
    def another_method(self):
        mock_socket = unittest.mock.Mock()
        mock_socket.recv.return_value = 'lalala'
        return mock_socket

    @patch('myhome.MyHomeSocket.initSocket', new=another_method)
    def test_3(self):
        self.assertTrue(self.my.initSocket())
        self.my.connect()
        self.assertEqual(self.my.receive(), 'lalala')


if __name__ == '__main__':
    unittest.main()
