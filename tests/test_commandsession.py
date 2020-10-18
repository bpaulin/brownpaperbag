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

    def wrapper_rcv(self, recv_data):
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

        return recv_side_effect

    def wrapper_send(self, sent_data):
        def send_side_effect(data):
            try:
                next_data = next(sent_data)
            except StopIteration:
                self.fail("unexpected sent data: %s" % data)
            if type(next_data) is not dict:
                self.assertEqual(next_data, data)
            elif next_data["assert"]:
                self.assertEqual(next_data["value"], data)
            asynctest.set_read_ready(self.socket_mock, self.loop)
            return len(data)

        return send_side_effect

    async def test_instance(self, mock_check):
        self.assertIsInstance(self.my, bpbgate.BpbCommandSession)

    async def test_cover_state(self, mock_check):
        self.socket_mock.recv.side_effect = self.wrapper_rcv(
            iter(
                (
                    b"*#*1##",
                    b"*98*2##",
                    b"*#00000000000000000000000000##",
                    b"*#00000000000000000000000000##",
                )
            )
        )
        self.socket_mock.send.side_effect = self.wrapper_send(
            iter(
                (
                    b"*#*1##",
                    b"*99*9##",
                    b"*#*1##",
                    {"value": b"*#*1##", "assert": False},
                    b"*#*1##",
                )
            )
        )
        self.assertTrue(await self.my.connect())

    async def test_cover_state2(self, mock_check):
        self.socket_mock.recv.side_effect = self.wrapper_rcv(
            iter((b"*2*0*10##", b"*#*1##"))
        )
        self.socket_mock.send.side_effect = self.wrapper_send(
            iter((b"*#*1##", b"*#2*10##"))
        )
        with patch.object(self.my, "_authent", return_value=True) as method:
            state = await self.my.get_cover_state("10")
            self.assertEqual(state, "0")


if __name__ == "__main__":
    unittest.main()
