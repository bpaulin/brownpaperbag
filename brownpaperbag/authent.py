"""Authentification helpers."""
import hashlib
import string
from random import SystemRandom

CLIENT_ID = "636F70653E"
SERVER_ID = "736F70653E"


def _digit_to_hex(string_of_digit):
    """Convert string of digits to string of hex."""
    return "".join(
        [
            hex(int(i))[2:]
            for i in [
                string_of_digit[i : i + 2] for i in range(0, len(string_of_digit), 2)
            ]
        ]
    )


def _hex_to_digit(toconvert):
    """Convert string of hex to strings of digits."""
    return "".join([str(int(i, 16)).zfill(2) for i in toconvert])


def _generate_random_rb():
    cryptogen = SystemRandom()
    return "".join(cryptogen.choice(string.ascii_letters) for x in range(20))


def generate_authent(nonce, pwd, client_random=None):
    """Return authentification string."""
    server_random = nonce[2:-2]
    server_random = _digit_to_hex(server_random)
    if not client_random:
        client_random = _generate_random_rb()
    client_random = hashlib.sha256(client_random.encode()).hexdigest()
    message = (
        server_random
        + client_random
        + SERVER_ID
        + CLIENT_ID
        + hashlib.sha256(pwd.encode()).hexdigest()
    )
    message = hashlib.sha256(message.encode()).hexdigest()
    return {
        "ra": server_random,
        "rb": client_random,
        "pwd": pwd,
        "client_response": "*#"
        + _hex_to_digit(client_random)
        + "*"
        + _hex_to_digit(message)
        + "##",
    }


def check_server_authent(client_authent, server_response):
    """Check server response."""
    expected = (
        client_authent["ra"]
        + client_authent["rb"]
        + hashlib.sha256(client_authent["pwd"].encode()).hexdigest()
    )
    expected = hashlib.sha256(expected.encode()).hexdigest()
    server_response = server_response[2:-2]
    return server_response == _hex_to_digit(expected)
