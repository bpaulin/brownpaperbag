# content of test_time.py
import pytest
from brownpaperbag import authent
from datetime import datetime, timedelta


def test_convert_digit_hex():
    s = "1401120915100305"
    h = authent._digit_to_hex(s)
    assert s == authent._hex_to_digit(h)
