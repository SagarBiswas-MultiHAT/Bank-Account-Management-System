import pytest

from bank_app.validation import parse_date, validate_date_of_birth, validate_mobile
from bank_app.errors import ValidationError


def test_parse_date_valid():
    parsed = parse_date("01/01/2000", "Date of birth")
    assert parsed.value.year == 2000


def test_parse_date_invalid():
    with pytest.raises(ValidationError):
        parse_date("2000-01-01", "Date of birth")


def test_validate_date_of_birth_rejects_future():
    with pytest.raises(ValidationError):
        validate_date_of_birth("01/01/2999")


def test_validate_mobile_accepts_10_digits():
    assert validate_mobile("1234567890") == "1234567890"


def test_validate_mobile_rejects_letters():
    with pytest.raises(ValidationError):
        validate_mobile("12345abcde")
