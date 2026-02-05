import pytest

from bank_app.security import hash_secret, verify_and_update


def test_hash_and_verify_round_trip():
    hashed = hash_secret("secret123")
    valid, new_hash = verify_and_update(hashed, "secret123")
    assert valid is True
    assert new_hash is None or isinstance(new_hash, str)


def test_hash_rejects_wrong_password():
    hashed = hash_secret("secret123")
    valid, new_hash = verify_and_update(hashed, "wrong")
    assert valid is False
    assert new_hash is None
