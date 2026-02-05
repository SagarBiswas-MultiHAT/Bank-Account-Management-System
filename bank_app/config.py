from __future__ import annotations

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(os.getenv("BANKAPP_DB_PATH", DATA_DIR / "bank.db"))

DATE_FORMAT = "%d/%m/%Y"

MIN_BALANCE = 10000
MAX_TRANSACTION = 25000

ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536  # 64 MiB
ARGON2_PARALLELISM = 2
ARGON2_HASH_LEN = 32
ARGON2_SALT_LEN = 16

PROTECTED_ADMIN_IDS = {"aayush"}

BOOTSTRAP_ADMIN_ID = os.getenv("BANKAPP_BOOTSTRAP_ADMIN_ID")
BOOTSTRAP_ADMIN_PASSWORD = os.getenv("BANKAPP_BOOTSTRAP_ADMIN_PASSWORD")
