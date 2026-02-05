from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from .config import DATE_FORMAT

SCHEMA = """
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
    account_number TEXT PRIMARY KEY,
    pin_hash TEXT NOT NULL,
    balance INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    name TEXT NOT NULL,
    account_type TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    mobile TEXT NOT NULL,
    gender TEXT NOT NULL,
    nationality TEXT NOT NULL,
    kyc_document TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number TEXT NOT NULL,
    amount INTEGER NOT NULL,
    tx_type TEXT NOT NULL,
    balance_after INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(account_number) REFERENCES customers(account_number) ON DELETE CASCADE
);
"""


class Storage:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def admin_exists(self, username: str | None = None) -> bool:
        with self.connect() as conn:
            if username:
                row = conn.execute(
                    "SELECT 1 FROM admins WHERE username = ?",
                    (username,),
                ).fetchone()
            else:
                row = conn.execute("SELECT 1 FROM admins LIMIT 1").fetchone()
            return row is not None

    def create_admin(self, username: str, password_hash: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO admins (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, password_hash, datetime.now().strftime(DATE_FORMAT)),
            )

    def get_admin_hash(self, username: str) -> str | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT password_hash FROM admins WHERE username = ?",
                (username,),
            ).fetchone()
            return row["password_hash"] if row else None

    def update_admin_hash(self, username: str, password_hash: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE admins SET password_hash = ? WHERE username = ?",
                (password_hash, username),
            )

    def delete_admin(self, username: str) -> int:
        with self.connect() as conn:
            cur = conn.execute("DELETE FROM admins WHERE username = ?", (username,))
            return cur.rowcount

    def customer_exists(self, account_number: str) -> bool:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM customers WHERE account_number = ?",
                (account_number,),
            ).fetchone()
            return row is not None

    def create_customer(
        self,
        account_number: str,
        pin_hash: str,
        balance: int,
        created_at: str,
        name: str,
        account_type: str,
        date_of_birth: str,
        mobile: str,
        gender: str,
        nationality: str,
        kyc_document: str,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO customers (
                    account_number, pin_hash, balance, created_at, name, account_type,
                    date_of_birth, mobile, gender, nationality, kyc_document
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_number,
                    pin_hash,
                    balance,
                    created_at,
                    name,
                    account_type,
                    date_of_birth,
                    mobile,
                    gender,
                    nationality,
                    kyc_document,
                ),
            )

    def get_customer(self, account_number: str) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM customers WHERE account_number = ?",
                (account_number,),
            ).fetchone()

    def get_customer_by_mobile(self, mobile: str) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM customers WHERE mobile = ?",
                (mobile,),
            ).fetchone()

    def get_customer_by_name(self, name: str) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM customers WHERE name = ? COLLATE NOCASE LIMIT 1",
                (name,),
            ).fetchone()

    def update_customer_pin(self, account_number: str, pin_hash: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE customers SET pin_hash = ? WHERE account_number = ?",
                (pin_hash, account_number),
            )

    def update_balance(self, account_number: str, new_balance: int) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE customers SET balance = ? WHERE account_number = ?",
                (new_balance, account_number),
            )

    def delete_customer(self, account_number: str) -> int:
        with self.connect() as conn:
            cur = conn.execute("DELETE FROM customers WHERE account_number = ?", (account_number,))
            return cur.rowcount

    def add_transaction(self, account_number: str, amount: int, tx_type: str, balance_after: int) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO transactions (account_number, amount, tx_type, balance_after, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (account_number, amount, tx_type, balance_after, datetime.now().strftime(DATE_FORMAT)),
            )

    def update_balance_with_transaction(
        self,
        account_number: str,
        delta: int,
        tx_type: str,
    ) -> int:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT balance FROM customers WHERE account_number = ?",
                (account_number,),
            ).fetchone()
            if row is None:
                raise ValueError("Account not found")
            new_balance = int(row["balance"]) + delta
            conn.execute(
                "UPDATE customers SET balance = ? WHERE account_number = ?",
                (new_balance, account_number),
            )
            conn.execute(
                """
                INSERT INTO transactions (account_number, amount, tx_type, balance_after, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (account_number, abs(delta), tx_type, new_balance, datetime.now().strftime(DATE_FORMAT)),
            )
            return new_balance
