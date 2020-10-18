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
        recv_data = iter(recv_data)
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
        sent_data = [b"*#*1##"] + sent_data
        sent_data = iter(sent_data)

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

    async def test_authenticate(self, mock_check):
        self.socket_mock.recv.side_effect = self.wrapper_rcv(
            [
                b"*#*1##",
                b"*98*2##",
                b"*#00000000000000000000000000##",
                b"*#00000000000000000000000000##",
            ]
        )
        self.socket_mock.send.side_effect = self.wrapper_send(
            [b"*99*9##", b"*#*1##", {"value": b"*#*1##", "assert": False}, b"*#*1##"]
        )
        self.assertTrue(await self.my.connect())

    async def __abstract_bpb_test(self, receive, sent, method, check):
        self.socket_mock.recv.side_effect = self.wrapper_rcv(receive)
        self.socket_mock.send.side_effect = self.wrapper_send(sent)
        with patch.object(self.my, "_authent", return_value=True):
            state = await method
            self.assertEqual(state, check)

    async def test_is_light_on(self, mock_check):
        await self.__abstract_bpb_test(
            [b"*1*0*10##", b"*#*1##"], [b"*#1*10##"], self.my.is_light_on("10"), False,
        )

    async def test_get_cover_state(self, mock_check):
        await self.__abstract_bpb_test(
            [b"*2*0*10##", b"*#*1##"],
            [b"*#2*10##"],
            self.my.get_cover_state("10"),
            "0",
        )

    async def test_open_cover(self, mock_check):
        await self.__abstract_bpb_test(
            [b"*2*1*10##", b"*#*1##"], [b"*2*1*10##"], self.my.open_cover("10"), True,
        )

    async def test_close_cover(self, mock_check):
        await self.__abstract_bpb_test(
            [b"*2*2*10##", b"*#*1##"], [b"*2*2*10##"], self.my.close_cover("10"), True,
        )

    async def test_stop_cover(self, mock_check):
        await self.__abstract_bpb_test(
            [b"*2*0*10##", b"*#*1##"], [b"*2*0*10##"], self.my.stop_cover("10"), True,
        )

    async def test_turn_on_light(self, mock_check):
        await self.__abstract_bpb_test(
            [b"*1*1*10##", b"*#*1##"],
            [b"*1*1*10##"],
            self.my.turn_on_light("10"),
            True,
        )

    async def test_turn_off_light(self, mock_check):
        await self.__abstract_bpb_test(
            [b"*1*0*10##", b"*#*1##"],
            [b"*1*0*10##"],
            self.my.turn_off_light("10"),
            True,
        )

    async def test_get_light_id(self, mock_check):
        await self.__abstract_bpb_test(
            [b"*1*0*10##*1*1*11##*1*0*12##*#*1##"],
            [b"*#1*0##"],
            self.my.get_light_ids(),
            {"10": "0", "11": "1", "12": "0"},
        )

    async def test_get_cover_id(self, mock_check):
        await self.__abstract_bpb_test(
            [b"*2*0*10##*2*1*11##*2*2*12##*#*1##"],
            [b"*#2*0##"],
            self.my.get_cover_ids(),
            {"10": "0", "11": "1", "12": "2"},
        )


if __name__ == "__main__":
    unittest.main()
