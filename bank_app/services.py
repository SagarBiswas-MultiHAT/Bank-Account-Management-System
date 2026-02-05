from __future__ import annotations

from datetime import date

from .config import (
    BOOTSTRAP_ADMIN_ID,
    BOOTSTRAP_ADMIN_PASSWORD,
    DATE_FORMAT,
    MAX_TRANSACTION,
    MIN_BALANCE,
    PROTECTED_ADMIN_IDS,
)
from .errors import AuthError, BusinessRuleError, ConflictError, NotFoundError, ValidationError
from .security import hash_secret, verify_and_update
from .storage import Storage
from .validation import (
    require_non_empty,
    validate_account_number,
    validate_account_type,
    validate_admin_id,
    validate_amount,
    validate_date_of_birth,
    validate_mobile,
    validate_pin,
    validate_password,
)


def _normalize_gender(gender: str) -> str:
    gender = require_non_empty(gender, "Gender")
    if gender not in {"Male", "Female"}:
        raise ValidationError("Gender must be Male or Female.")
    return gender


class BankService:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.storage.init_db()
        self._bootstrap_admin()

    @classmethod
    def create_default(cls, db_path) -> "BankService":
        return cls(Storage(db_path))

    def _bootstrap_admin(self) -> None:
        if self.storage.admin_exists():
            return
        if BOOTSTRAP_ADMIN_ID and BOOTSTRAP_ADMIN_PASSWORD:
            self.create_admin(BOOTSTRAP_ADMIN_ID, BOOTSTRAP_ADMIN_PASSWORD)

    def admin_exists(self, admin_id: str | None = None) -> bool:
        return self.storage.admin_exists(admin_id)

    def create_admin(self, admin_id: str, password: str) -> None:
        admin_id = validate_admin_id(admin_id)
        password = validate_password(password, "Password")
        if self.storage.admin_exists(admin_id):
            raise ConflictError("Admin ID is already in use.")
        self.storage.create_admin(admin_id, hash_secret(password))

    def authenticate_admin(self, admin_id: str, password: str) -> bool:
        admin_id = validate_admin_id(admin_id)
        password = require_non_empty(password, "Password")
        stored_hash = self.storage.get_admin_hash(admin_id)
        if stored_hash is None:
            return False
        valid, new_hash = verify_and_update(stored_hash, password)
        if valid and new_hash:
            self.storage.update_admin_hash(admin_id, new_hash)
        return valid

    def delete_admin(self, admin_id: str, current_admin_id: str | None = None) -> None:
        admin_id = validate_admin_id(admin_id)
        if current_admin_id and admin_id == current_admin_id:
            raise BusinessRuleError("You cannot delete the currently logged-in admin.")
        if admin_id in PROTECTED_ADMIN_IDS:
            raise BusinessRuleError("This admin account is protected.")
        removed = self.storage.delete_admin(admin_id)
        if removed == 0:
            raise NotFoundError("Admin account not found.")

    def customer_exists(self, account_number: str) -> bool:
        account_number = validate_account_number(account_number)
        return self.storage.customer_exists(account_number)

    def _get_customer_account_number_for_identifier(self, identifier: str) -> str | None:
        identifier = require_non_empty(identifier, "Identifier")
        account_candidate = None
        try:
            account_candidate = validate_account_number(identifier)
        except ValidationError:
            account_candidate = None
        if account_candidate and self.storage.get_customer(account_candidate):
            return account_candidate

        mobile_candidate = None
        try:
            mobile_candidate = validate_mobile(identifier)
        except ValidationError:
            mobile_candidate = None
        if mobile_candidate:
            customer = self.storage.get_customer_by_mobile(mobile_candidate)
            if customer is not None:
                return customer["account_number"]

        customer = self.storage.get_customer_by_name(identifier)
        if customer is not None:
            return customer["account_number"]

        return None

    def create_customer(
        self,
        account_number: str,
        name: str,
        account_type: str,
        date_of_birth: str,
        mobile: str,
        gender: str,
        nationality: str,
        kyc_document: str,
        pin: str,
        initial_balance: str,
    ) -> None:
        account_number = validate_account_number(account_number)
        name = require_non_empty(name, "Name")
        account_type = validate_account_type(account_type)
        date_of_birth = validate_date_of_birth(date_of_birth)
        mobile = validate_mobile(mobile)
        gender = _normalize_gender(gender)
        nationality = require_non_empty(nationality, "Nationality")
        kyc_document = require_non_empty(kyc_document, "KYC document")
        pin = validate_pin(pin)
        balance = validate_amount(initial_balance)

        if self.storage.customer_exists(account_number):
            raise ConflictError("Account number is already allocated.")
        if balance < MIN_BALANCE:
            raise BusinessRuleError(f"Initial balance must be at least {MIN_BALANCE}.")

        today = date.today().strftime(DATE_FORMAT)
        self.storage.create_customer(
            account_number=account_number,
            pin_hash=hash_secret(pin),
            balance=balance,
            created_at=today,
            name=name,
            account_type=account_type,
            date_of_birth=date_of_birth,
            mobile=mobile,
            gender=gender,
            nationality=nationality,
            kyc_document=kyc_document,
        )

    def authenticate_customer(self, account_number: str, pin: str) -> bool:
        account_number = validate_account_number(account_number)
        pin = require_non_empty(pin, "PIN")
        customer = self.storage.get_customer(account_number)
        if customer is None:
            return False
        valid, new_hash = verify_and_update(customer["pin_hash"], pin)
        if valid and new_hash:
            self.storage.update_customer_pin(account_number, new_hash)
        return valid

    def authenticate_customer_with_identifier(self, identifier: str, pin: str) -> str | None:
        account_number = self._get_customer_account_number_for_identifier(identifier)
        if account_number is None:
            return None
        if self.authenticate_customer(account_number, pin):
            return account_number
        return None

    def change_pin(self, account_number: str, new_pin: str) -> None:
        account_number = validate_account_number(account_number)
        new_pin = validate_pin(new_pin)
        if not self.storage.customer_exists(account_number):
            raise NotFoundError("Account not found.")
        self.storage.update_customer_pin(account_number, hash_secret(new_pin))

    def delete_customer(self, account_number: str) -> None:
        account_number = validate_account_number(account_number)
        removed = self.storage.delete_customer(account_number)
        if removed == 0:
            raise NotFoundError("Account not found.")

    def get_balance(self, account_number: str) -> int:
        account_number = validate_account_number(account_number)
        customer = self.storage.get_customer(account_number)
        if customer is None:
            raise NotFoundError("Account not found.")
        return int(customer["balance"])

    def get_customer_summary(self, account_number: str) -> dict:
        account_number = validate_account_number(account_number)
        customer = self.storage.get_customer(account_number)
        if customer is None:
            raise NotFoundError("Account not found.")
        return {
            "account_number": customer["account_number"],
            "balance": int(customer["balance"]),
            "created_at": customer["created_at"],
            "name": customer["name"],
            "account_type": customer["account_type"],
            "date_of_birth": customer["date_of_birth"],
            "mobile": customer["mobile"],
            "gender": customer["gender"],
            "nationality": customer["nationality"],
            "kyc_document": customer["kyc_document"],
        }

    def deposit(self, account_number: str, amount: str) -> int:
        account_number = validate_account_number(account_number)
        amount_value = validate_amount(amount)
        if amount_value > MAX_TRANSACTION:
            raise BusinessRuleError("Limit exceeded.")
        if not self.storage.customer_exists(account_number):
            raise NotFoundError("Account not found.")
        new_balance = self.storage.update_balance_with_transaction(
            account_number, amount_value, "deposit"
        )
        return new_balance

    def withdraw(self, account_number: str, amount: str) -> int:
        account_number = validate_account_number(account_number)
        amount_value = validate_amount(amount)
        if amount_value > MAX_TRANSACTION:
            raise BusinessRuleError("Limit exceeded.")
        customer = self.storage.get_customer(account_number)
        if customer is None:
            raise NotFoundError("Account not found.")
        current_balance = int(customer["balance"])
        new_balance = current_balance - amount_value
        if new_balance < MIN_BALANCE:
            raise BusinessRuleError("Minimum balance requirement not met.")
        new_balance = self.storage.update_balance_with_transaction(
            account_number, -amount_value, "withdraw"
        )
        return new_balance

    def require_admin_auth(self, admin_id: str, password: str) -> None:
        if not self.authenticate_admin(admin_id, password):
            raise AuthError("Invalid admin credentials.")

    def require_customer_auth(self, account_number: str, pin: str) -> None:
        if not self.authenticate_customer(account_number, pin):
            raise AuthError("Invalid customer credentials.")
