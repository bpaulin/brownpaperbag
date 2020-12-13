"""BrownPaperBag."""

import asyncio
import logging
import re

from brownpaperbag.authent import generate_authent, check_server_authent

SESSION_EVENT = "*99*1##"
SESSION_COMMAND = "*99*9##"

ACK = "*#*1##"
NACK = "*#*0##"

AUTHENT_HMAC_SHA2 = "*98*2##"

COVER_STOPPED = "0"
COVER_OPENING = "1"
COVER_CLOSING = "2"

ON = "1"
OFF = "0"


class BpbGate:
    """Manage communication with myhomeserver1."""

    TIMEOUT = 3
    _logger = None  # type: logging.Logger
    _writer = None  # type: asyncio.StreamWriter
    _reader = None  # type: asyncio.StreamReader

    def __init__(self, host, port, pwd):
        """Constructor."""
        self._connection_data = {
            "host": host,
            "port": port,
            "pwd": pwd,
        }
        self._pwd = pwd
        self.lock = asyncio.Lock()
        self._sock = None

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

    def set_socket(self, sock):
        """Allow override of socket."""
        self._sock = sock

    async def _readuntil(self, separator):
        try:
            data = await self._reader.readuntil(separator.encode())
        except asyncio.IncompleteReadError as ex:
            self.logger.warning(
                "'%s' expected, received '%s'", separator, ex.partial.decode()
            )
            if ex.partial.decode() == NACK:
                return False
            raise
        response = data.decode()
        self.logger.debug("received: %s", response)
        return response

    def _write(self, command):
        self._writer.write(command.encode())
        self.logger.debug("sent: %s", command)

    async def _open_session(self, session=SESSION_COMMAND):
        """Initialize Connection."""
        self.logger.info("Connecting")
        try:
            if self._sock:
                self._reader, self._writer = await asyncio.open_connection(
                    sock=self._sock
                )
                self._write(ACK)
            else:  # pragma: no cover
                self._reader, self._writer = await asyncio.open_connection(
                    self._connection_data["host"], self._connection_data["port"]
                )
        except OSError as err:
            raise ConnectionError(err) from err
        return await self._authent(session)

    async def _authent(self, session):
        # receive hello
        hello = await self._readuntil("##")
        if hello != ACK:
            self._writer.close()
            await self._writer.wait_closed()
            raise ConnectionAbortedError("Unexpected answer")
        self.logger.info("Connected")

        self.logger.info("Authenticating")
        # send session
        self._write(session)
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
        client_authent = generate_authent(nonce, self._pwd)
        self._write(client_authent["client_response"])
        # check authent
        server_response = await self._readuntil("##")
        if not check_server_authent(client_authent, server_response):
            raise ConnectionAbortedError("Unexpected confirmation from server")
        self._write(ACK)

        self.logger.info("Authenticated")
        return True

    async def connect(self):
        """Create connection."""
        await self._open_session()
        return True

    async def send_raw(self, command):
        """Send a command to the gateway."""
        async with self.lock:
            if self._reader is None or self._reader.at_eof():
                await self.connect()
            self._write(command)
            data = await self._readuntil(ACK)
            if not data:
                # retry
                self._write(command)
                data = await self._readuntil(ACK)
            return data


class BpbCommandSession(BpbGate):
    """ Command session with myHomeserver1 """

    async def send_command(self, who, what, where):
        """Send a command to the gateway."""
        command = "*%s*%s*%s##" % (who, what, where)
        return await self.send_raw(command)

    async def send_request(self, who, where):
        """Send a request to the gateway."""
        command = "*#%s*%s##" % (who, where)
        return await self.send_raw(command)

    async def send_list(self, who):
        """Send a request to the gateway."""
        command = "*#%s*0##" % (who)
        data = await self.send_raw(command)
        pattern = re.compile(r"\*\d+\*\d+\*\d+")
        items = pattern.findall(data)
        pattern = re.compile(r"\d+")
        hitems = {}
        for item in items:
            (who, what, where) = pattern.findall(item)
            hitems[where] = what
        return hitems

    async def get_light_ids(self):
        """Return list of all lights ids."""
        self.logger.info("polling lights")
        return await self.send_list("1")

    async def get_cover_ids(self):
        """Return list of all cover ids."""
        self.logger.info("polling covers")
        return await self.send_list("2")

    async def turn_on_light(self, where):
        """Turn on a light by Id."""
        response = await self.send_command("1", "1", where)
        return response[3] == ON

    async def turn_off_light(self, where):
        """Turn off a light by Id."""
        response = await self.send_command("1", "0", where)
        return response[3] == OFF

    async def is_light_on(self, where):
        """Return light status by Id."""
        response = response = await self.send_request("1", where)
        return response[3] == ON

    async def open_cover(self, where):
        """Open a cover by Id."""
        response = await self.send_command("2", COVER_OPENING, where)
        return response[3] == COVER_OPENING

    async def close_cover(self, where):
        """Close a cover by Id."""
        response = await self.send_command("2", COVER_CLOSING, where)
        return response[3] == COVER_CLOSING

    async def stop_cover(self, where):
        """Stop a cover by Id."""
        response = await self.send_command("2", COVER_STOPPED, where)
        return response[3] == COVER_STOPPED

    async def get_cover_state(self, where):
        """Return cover status by Id."""
        response = await self.send_request("2", where)
        return response[3]


class BpbEventSession(BpbGate):
    """ Event session with myHomeserver1 """

    async def connect(self):
        """Create connection."""
        await self._open_session(SESSION_EVENT)
        return True

    async def readevent(self, separator="##"):
        """Listen to gateway events."""
        data = await self._reader.readuntil(separator.encode())
        response = data.decode()
        self.logger.debug("received: %s", response)
        return response

    async def readevent_exploded(self):
        """Listen to gateway events."""
        response = await self.readevent()
        (who, what, where) = re.search(r"\*(.*)\*(.*)\*(.*)##", response).groups()
        if what.startswith("1000#"):
            what = what.replace("1000#", "")
        return who, what, where
