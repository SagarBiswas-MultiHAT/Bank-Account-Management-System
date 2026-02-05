from __future__ import annotations

from argon2 import PasswordHasher, Type
from argon2 import exceptions as argon2_exceptions

from .config import (
    ARGON2_HASH_LEN,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    ARGON2_SALT_LEN,
    ARGON2_TIME_COST,
)

_hasher = PasswordHasher(
    time_cost=ARGON2_TIME_COST,
    memory_cost=ARGON2_MEMORY_COST,
    parallelism=ARGON2_PARALLELISM,
    hash_len=ARGON2_HASH_LEN,
    salt_len=ARGON2_SALT_LEN,
    type=Type.ID,
)


def hash_secret(secret: str) -> str:
    return _hasher.hash(secret)


def verify_and_update(stored_hash: str, secret: str) -> tuple[bool, str | None]:
    try:
        valid = _hasher.verify(stored_hash, secret)
    except argon2_exceptions.VerifyMismatchError:
        return False, None
    except argon2_exceptions.VerificationError:
        return False, None

    if not valid:
        return False, None

    if _hasher.check_needs_rehash(stored_hash):
        return True, _hasher.hash(secret)

    return True, None
