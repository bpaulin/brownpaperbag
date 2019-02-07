# content of test_time.py
import pytest
from brownpaperbag import authent
from datetime import datetime, timedelta

testdata = [
    (datetime(2001, 12, 12), datetime(2001, 12, 11), timedelta(1)),
    (datetime(2001, 12, 11), datetime(2001, 12, 12), timedelta(-1)),
]

@pytest.mark.parametrize("a,b,expected", testdata)
def test_timedistance_v0(a, b, expected):
    diff = a - b
    assert diff == expected

def test_convert_digit_hex():
    s = '1401120915100305'
    h = authent._digit_to_hex(s)
    assert s == authent._hex_to_digit(h)
