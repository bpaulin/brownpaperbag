import hashlib

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


def generate_authent(nonce, pwd):
    ra = nonce[2:-2]
    ra = _digit_to_hex(ra)
    # @todo random string
    rb = hashlib.sha256("rb".encode()).hexdigest()
    message = ra + rb + SERVER_ID + CLIENT_ID + hashlib.sha256(pwd.encode()).hexdigest()
    message = hashlib.sha256(message.encode()).hexdigest()
    return "*#" + _hex_to_digit(rb) + "*" + _hex_to_digit(message) + "##"
