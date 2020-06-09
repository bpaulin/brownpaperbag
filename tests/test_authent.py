# content of test_time.py
import pytest
from brownpaperbag import authent
from datetime import datetime, timedelta

VALID_PARAMS = {
    "nonce": "*#02000314150304060013131006110815150615091405090400021413081501010501090312041402151400131409111112130303100602050504030715110105##",
    "password": "azerty123",
    "rb": "01234567890123456789",
    "client_response": "*#04140706101308030504040601040307120004141509110911020402050400110604000613070802151502120315110208101513101105110402031508081514*05050001021215001503051000021215111412151002000810010600010301150800120007061400090312001104091502130311040403130812110511001215##",
    "server_response": "*#09050908071313011009060510000100090607041205031002140513151007131113041101100105001514141503080210020105151101100400140900081007##",
}


def test_convert_digit_hex():
    s = "1401120915100305"
    h = authent._digit_to_hex(s)
    assert s == authent._hex_to_digit(h)


def test_generate_authent():
    nonce = VALID_PARAMS["nonce"]
    password = VALID_PARAMS["password"]
    rb = VALID_PARAMS["rb"]
    client = authent.generate_authent(nonce, password, rb)
    assert client["client_response"] == VALID_PARAMS["client_response"]

    server = authent.check_server_authent(client, VALID_PARAMS["server_response"],)
    assert True == server


def test_generate_authent_without_rb():
    nonce = VALID_PARAMS["nonce"]
    password = VALID_PARAMS["password"]
    client = authent.generate_authent(nonce, password)
    assert client["rb"] != None


def test_generate_random_rb():
    rb1 = authent._generate_random_rb()
    assert 20 == len(rb1)
    rb2 = authent._generate_random_rb()
    assert 20 == len(rb2)
    assert rb1 != rb2
