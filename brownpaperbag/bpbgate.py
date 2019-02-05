"""BrownPaperBag."""

import logging
import asyncio
from brownpaperbag import authent

SESSION_EVENT = "*99*1##"
SESSION_COMMAND = "*99*9##"

ACK = "*#*1##"
NACK = "*#*0##"

COVER_STOPPED = 0
COVER_OPENING = 1
COVER_CLOSING = 2

ON = '1'
OFF = '0'


class BpbGate:
    """Manage communication with myhomeserver1."""

    ENCODING = 'utf-8'
    TIMEOUT = 3
    _socket = None
    _logger = None
    _light_ids = None
    _cover_ids = None
    _writer = None
    _reader = None

    def __init__(self, host, port, pwd):
        """Constructor."""
        self._host = host
        self._port = port
        self._pwd = pwd
        self.lock = asyncio.Lock()

    @property
    def logger(self):
        """Return logger, set it if needed."""
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    @logger.setter
    def logger(self, logger: logging.getLoggerClass()):
        """Allow override of logger."""
        self._logger = logger

    async def connect(self):
        await self.command_session()
        return True

    async def _readuntil(self, separator):
        data = await self._reader.readuntil(separator.encode())
        response = data.decode()
        self.logger.debug('received: '+response)
        return response

    def _write(self, command):
        self._writer.write(command.encode())
        self.logger.debug('sent: '+command)

    async def command_session(self):
        self._reader, self._writer = await asyncio.open_connection(
            self._host,
            self._port
        )
        # receive hello
        await self._readuntil('##')
        # send session
        self._write(SESSION_COMMAND)
        await self._readuntil('##')
        # say ok
        self._write(ACK)
        nonce = await self._readuntil('##')
        # send authent
        key = authent.generate_authent(nonce, self._pwd)
        self._write(key)
        await self._readuntil('##')
        # say ok
        self._write(ACK)

        return True

    async def send_command(self, who, what, where):
        command = f"*{who}*{what}*{where}##"
        async with self.lock:
            if self._reader is None or self._reader.at_eof():
                await self.command_session()
            self._write(command)
            data = await self._readuntil(ACK)
            return data

    async def send_request(self, who, where):
        command = f"*#{who}*{where}##"
        async with self.lock:
            if self._reader is None or self._reader.at_eof():
                await self.command_session()
            self._write(command)
            data = await self._readuntil(ACK)
            return data

    async def turn_on_light(self, where):
        await self.send_command('1', '1', where)

    async def turn_off_light(self, where):
        await self.send_command('1', '0', where)

    async def is_light_on(self, where):
        response = await self.send_request('1', where)
        return response[3] == ON

    async def open_cover(self, where):
        await self.send_command('2', COVER_OPENING, where)

    async def close_cover(self, where):
        await self.send_command('2', COVER_CLOSING, where)

    async def stop_cover(self, where):
        await self.send_command('2', COVER_STOPPED, where)

    async def get_cover_state(self, where):
        response = await self.send_request('2', where)
        return response[3]
