from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from bank_app.config import DB_PATH
from bank_app.errors import ServiceError
from bank_app.services import BankService


def parse_records(lines: list[str]) -> list[list[str]]:
    records: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line == "*":
            if current:
                records.append(current)
                current = []
            continue
        current.append(line)
    if current:
        records.append(current)
    return records


def migrate_admins(service: BankService, path: Path) -> None:
    if not path.exists():
        print(f"No admin file found at {path}")
        return
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for record in parse_records(lines):
        if len(record) < 2:
            continue
        admin_id, password = record[0], record[1]
        try:
            service.create_admin(admin_id, password)
            print(f"Imported admin: {admin_id}")
        except ServiceError as exc:
            print(f"Skipped admin {admin_id}: {exc}")


def migrate_customers(service: BankService, path: Path) -> None:
    if not path.exists():
        print(f"No customer file found at {path}")
        return
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for record in parse_records(lines):
        if len(record) < 11:
            continue
        (
            account_number,
            pin,
            balance,
            _created_at,
            name,
            account_type,
            date_of_birth,
            mobile,
            gender,
            nationality,
            kyc_document,
            *_rest,
        ) = record
        try:
            service.create_customer(
                account_number=account_number,
                name=name,
                account_type=account_type,
                date_of_birth=date_of_birth,
                mobile=mobile,
                gender=gender,
                nationality=nationality,
                kyc_document=kyc_document,
                pin=pin,
                initial_balance=balance,
            )
            print(f"Imported customer: {account_number}")
        except ServiceError as exc:
            print(f"Skipped customer {account_number}: {exc}")


def main() -> None:
    service = BankService.create_default(DB_PATH)
    migrate_admins(service, Path("database/Admin/adminDatabase.txt"))
    migrate_customers(service, Path("database/Customer/customerDatabase.txt"))
    print("Migration complete.")


if __name__ == "__main__":
    main()
