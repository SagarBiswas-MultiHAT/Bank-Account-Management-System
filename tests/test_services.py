import pytest

from bank_app.config import MIN_BALANCE
from bank_app.errors import BusinessRuleError, ConflictError
from bank_app.services import BankService


def make_service(tmp_path):
    db_path = tmp_path / "bank_test.db"
    return BankService.create_default(db_path)


def test_admin_lifecycle(tmp_path):
    service = make_service(tmp_path)
    assert service.admin_exists() is False
    service.create_admin("admin", "pass123")
    assert service.admin_exists() is True
    assert service.authenticate_admin("admin", "pass123") is True
    assert service.authenticate_admin("admin", "wrong") is False


def test_admin_duplicate(tmp_path):
    service = make_service(tmp_path)
    service.create_admin("admin", "pass123")
    with pytest.raises(ConflictError):
        service.create_admin("admin", "pass123")


def test_customer_deposit_withdraw(tmp_path):
    service = make_service(tmp_path)
    service.create_customer(
        account_number="12345",
        name="Test User",
        account_type="Savings",
        date_of_birth="01/01/2000",
        mobile="1234567890",
        gender="Male",
        nationality="Testland",
        kyc_document="Passport",
        pin="1234",
        initial_balance=str(MIN_BALANCE),
    )

    balance = service.deposit("12345", "1000")
    assert balance == MIN_BALANCE + 1000

    balance = service.withdraw("12345", "500")
    assert balance == MIN_BALANCE + 500

    with pytest.raises(BusinessRuleError):
        service.withdraw("12345", str(MIN_BALANCE + 1000))


def test_change_pin(tmp_path):
    service = make_service(tmp_path)
    service.create_customer(
        account_number="55555",
        name="Test User",
        account_type="Savings",
        date_of_birth="01/01/2000",
        mobile="1234567890",
        gender="Male",
        nationality="Testland",
        kyc_document="Passport",
        pin="1234",
        initial_balance=str(MIN_BALANCE),
    )
    assert service.authenticate_customer("55555", "1234") is True
    service.change_pin("55555", "9999")
    assert service.authenticate_customer("55555", "9999") is True


def test_customer_identifier_login(tmp_path):
    service = make_service(tmp_path)
    service.create_customer(
        account_number="98765",
        name="Unique User",
        account_type="Savings",
        date_of_birth="01/01/2000",
        mobile="9998887776",
        gender="Female",
        nationality="Testland",
        kyc_document="Passport",
        pin="1212",
        initial_balance=str(MIN_BALANCE),
    )

    assert service.authenticate_customer_with_identifier("Unique User", "1212") == "98765"
    assert service.authenticate_customer_with_identifier("unique user", "1212") == "98765"
    assert service.authenticate_customer_with_identifier("9998887776", "1212") == "98765"
    assert service.authenticate_customer_with_identifier("9998887776", "0000") is None
    assert service.authenticate_customer_with_identifier("no match", "1212") is None
