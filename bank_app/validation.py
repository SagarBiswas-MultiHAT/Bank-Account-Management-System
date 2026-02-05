from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from .config import DATE_FORMAT
from .errors import ValidationError


@dataclass(frozen=True)
class ParsedDate:
    raw: str
    value: date


def require_non_empty(value: str, field_name: str) -> str:
    if value is None or str(value).strip() == "":
        raise ValidationError(f"{field_name} cannot be empty.")
    return str(value).strip()


def validate_account_number(account_number: str) -> str:
    account_number = require_non_empty(account_number, "Account number")
    if not account_number.isdigit():
        raise ValidationError("Account number must be numeric.")
    return account_number


def validate_admin_id(admin_id: str) -> str:
    admin_id = require_non_empty(admin_id, "Admin ID")
    return admin_id


def validate_password(password: str, field_name: str = "Password") -> str:
    password = require_non_empty(password, field_name)
    if len(password) < 6:
        raise ValidationError(f"{field_name} must be at least 6 characters.")
    return password


def validate_pin(pin: str) -> str:
    pin = require_non_empty(pin, "PIN")
    if not pin.isdigit() or len(pin) != 4:
        raise ValidationError("PIN must be exactly 4 digits.")
    return pin


def validate_account_type(account_type: str) -> str:
    account_type = require_non_empty(account_type, "Account type")
    if account_type not in {"Savings", "Current"}:
        raise ValidationError("Account type must be Savings or Current.")
    return account_type


def validate_mobile(mobile: str) -> str:
    mobile = require_non_empty(mobile, "Mobile number")
    if not mobile.isdigit() or len(mobile) not in {10, 11}:
        raise ValidationError("Mobile number must be 10 or 11 digits.")
    return mobile


def parse_date(value: str, field_name: str) -> ParsedDate:
    value = require_non_empty(value, field_name)
    try:
        parsed = datetime.strptime(value, DATE_FORMAT).date()
    except ValueError as exc:
        raise ValidationError(f"{field_name} must match format {DATE_FORMAT}.") from exc
    return ParsedDate(raw=value, value=parsed)


def validate_date_of_birth(value: str) -> str:
    parsed = parse_date(value, "Date of birth")
    today = date.today()
    if parsed.value > today:
        raise ValidationError("Date of birth cannot be in the future.")
    if parsed.value.year < 1900:
        raise ValidationError("Date of birth must be after 1900.")
    return parsed.raw


def validate_amount(amount: str) -> int:
    amount = require_non_empty(amount, "Amount")
    if not amount.isdigit():
        raise ValidationError("Amount must be a positive whole number.")
    return int(amount)
