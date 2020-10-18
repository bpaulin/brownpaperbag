import asyncio
import logging
import socket
from unittest.mock import Mock

import asynctest
from asynctest import patch
from brownpaperbag import bpbgate


@patch("brownpaperbag.bpbgate.check_server_authent", return_value=True)
class CommandSessionTestCase(asynctest.TestCase):
    def setUp(self):
        self.my = bpbgate.BpbCommandSession("192.168.1.**", 20000, "*******")
        self.socket_mock = asynctest.SocketMock()
        self.socket_mock.type = socket.SOCK_STREAM
        self.my.set_socket(self.socket_mock)

    async def test_instance(self, mock_check):
        self.assertIsInstance(self.my, bpbgate.BpbCommandSession)

    async def test_cover_state(self, mock_check):
        # mock_check.return_value = True
        recv_data = iter(
            (
                b"*#*1##",
                b"*98*2##",
                b"*#00000000000000000000000000##",
                b"*#00000000000000000000000000##",
            )
        )

        recv_buffer = bytearray()

        def recv_side_effect(max_bytes):
            nonlocal recv_buffer

            if not recv_buffer:
                try:
                    recv_buffer.extend(next(recv_data))
                    asynctest.set_read_ready(self.socket_mock, self.loop)
                except StopIteration:
                    # nothing left
                    pass

            data = recv_buffer[:max_bytes]
            recv_buffer = recv_buffer[max_bytes:]

            if recv_buffer:
                # Some more data to read
                asynctest.set_read_ready(self.socket_mock, self.loop)

            return data

        def send_side_effect(data):
            print(data)
            asynctest.set_read_ready(self.socket_mock, self.loop)
            return len(data)

        self.socket_mock.recv.side_effect = recv_side_effect
        self.socket_mock.send.side_effect = send_side_effect
        self.assertTrue(await self.my.connect())

    async def test_cover_state2(self, mock_check):
        socket_mock = asynctest.SocketMock()
        socket_mock.type = socket.SOCK_STREAM
        recv_data = iter((b"*2*0*10##", b"*#*1##"))
        sent_data = iter((b"*#*1##", b"*#2*10##"))

        recv_buffer = bytearray()

        def recv_side_effect(max_bytes):
            nonlocal recv_buffer

            if not recv_buffer:
                try:
                    recv_buffer.extend(next(recv_data))
                    asynctest.set_read_ready(socket_mock, self.loop)
                except StopIteration:
                    # nothing left
                    pass

            data = recv_buffer[:max_bytes]
            recv_buffer = recv_buffer[max_bytes:]

            if recv_buffer:
                asynctest.set_read_ready(socket_mock, self.loop)

            return data

        def send_side_effect(data):
            self.assertEqual(next(sent_data), data)
            asynctest.set_read_ready(socket_mock, self.loop)
            return len(data)

        socket_mock.recv.side_effect = recv_side_effect
        socket_mock.send.side_effect = send_side_effect
        self.my.set_socket(socket_mock)
        with patch.object(self.my, "_authent", return_value=True) as method:
            state = await self.my.get_cover_state("10")
            self.assertEqual(state, "0")


if __name__ == "__main__":
    unittest.main()
