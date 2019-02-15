"""BrownPaperBag."""

import asyncio
import logging

from brownpaperbag import authent

SESSION_EVENT = "*99*1##"
SESSION_COMMAND = "*99*9##"

ACK = "*#*1##"
NACK = "*#*0##"

AUTHENT_HMAC_SHA2 = "*98*2##"

COVER_STOPPED = 0
COVER_OPENING = 1
COVER_CLOSING = 2

ON = "1"
OFF = "0"


class BpbGate:
    """Manage communication with myhomeserver1."""

    ENCODING = "utf-8"
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
        """Create connection."""
        await self.command_session()
        return True

    async def _readuntil(self, separator):
        data = await self._reader.readuntil(separator.encode())
        response = data.decode()
        self.logger.debug("received: " + response)
        return response

    def _write(self, command):
        self._writer.write(command.encode())
        self.logger.debug("sent: " + command)

    async def command_session(self):
        """Initialize Connection."""
        self.logger.info("Connecting")
        try:
            self._reader, self._writer = await asyncio.open_connection(
                self._host, self._port
            )
        except OSError as err:
            raise ConnectionError(err)
        # receive hello
        hello = await self._readuntil("##")
        if hello != ACK:
            self._writer.close()
            await self._writer.wait_closed()
            raise ConnectionAbortedError("Unexpected answer")
        self.logger.info("Connected")

        self.logger.info("Authenticating")
        # send session
        self._write(SESSION_COMMAND)
        # Receive authent method
        authent_method = await self._readuntil("##")
        if authent_method == AUTHENT_HMAC_SHA2:
            self.logger.info("hmac sha2 asked")
        else:
            raise NotImplementedError("Authentification method not implemented")
        # say ok
        self._write(ACK)
        nonce = await self._readuntil("##")
        # send authent
        client_authent = authent.generate_authent(nonce, self._pwd)
        self._write(client_authent["client_response"])
        # check authent
        server_response = await self._readuntil("##")
        if not authent.check_server_authent(client_authent, server_response):
            raise ConnectionAbortedError("Unexpected confirmation from server")
        # say ok
        self._write(ACK)

        self.logger.info("Authenticated")
        return True

    async def send_command(self, who, what, where):
        """Send a command to the gateway."""
        command = "*%s*%s*%s##" % (who, what, where)
        async with self.lock:
            if self._reader is None or self._reader.at_eof():
                await self.command_session()
            self._write(command)
            data = await self._readuntil(ACK)
            return data

    async def send_request(self, who, where):
        """Send a request to the gateway."""
        command = "*#%s*%s##" % (who, where)
        async with self.lock:
            if self._reader is None or self._reader.at_eof():
                await self.command_session()
            self._write(command)
            data = await self._readuntil(ACK)
            return data

    async def turn_on_light(self, where):
        """Turn on a light by Id."""
        await self.send_command("1", "1", where)

    async def turn_off_light(self, where):
        """Turn off a light by Id."""
        await self.send_command("1", "0", where)

    async def is_light_on(self, where):
        """Return light status by Id."""
        response = await self.send_request("1", where)
        return response[3] == ON

    async def open_cover(self, where):
        """Open a cover by Id."""
        await self.send_command("2", COVER_OPENING, where)

    async def close_cover(self, where):
        """Close a cover by Id."""
        await self.send_command("2", COVER_CLOSING, where)

    async def stop_cover(self, where):
        """Stop a cover by Id."""
        await self.send_command("2", COVER_STOPPED, where)

    async def get_cover_state(self, where):
        """Return cover status by Id."""
        response = await self.send_request("2", where)
        return response[3]