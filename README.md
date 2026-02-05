# Bank Account Management System (Tkinter + SQLite + Argon2id)

A desktop Bank Account Management System built with Python and Tkinter. It supports admin and customer workflows, stores data in SQLite, and secures credentials with **Argon2id** hashing. The UI is intentionally simple and fast, while the backend focuses on correctness and safety.

If you read only this README, you should understand how the system works, how the data is stored, and how to operate or extend it.

---

<details>

<summary>Pictures</summary>

<br>

![](https://imgur.com/yxAGTh6.png)

---

![](https://imgur.com/yltojjy.png)

---

![](https://imgur.com/jakFCbb.png)

---

![](https://imgur.com/4Z3CZZw.png)

---

![](https://imgur.com/EA7m0LH.png)

---

![](https://imgur.com/RU5u0AO.png)

---

![](https://imgur.com/cEwk8Ch.png)

---

</details>

## What This App Does

**Admin features**
- Create and delete admin accounts
- Create and delete customer accounts
- View customer account summaries

**Customer features**
- Secure login with PIN
- Deposit and withdraw funds (with limits)
- Change PIN
- View balance and account summary
- Close account

**Security highlights**
- Admin passwords and customer PINs are hashed with **Argon2id**
- SQLite storage (no plaintext credentials)
- Input validation at the service layer
- Transaction updates are atomic

---

## Architecture Overview

The project is split into clear layers:

- **UI layer**: `bank_app/ui.py`
  - Tkinter windows and user interactions
- **Service layer**: `bank_app/services.py`
  - Business rules, validation, and security
- **Storage layer**: `bank_app/storage.py`
  - SQLite schema and persistence
- **Security**: `bank_app/security.py`
  - Argon2id hashing and verification

This separation makes the code easier to test, reason about, and change safely.

---

## Data Model (SQLite)

The app stores data in `data/bank.db` with three tables:

**admins**
- `username` (unique)
- `password_hash`
- `created_at`

**customers**
- `account_number` (primary key)
- `pin_hash`
- `balance` (integer)
- `created_at`
- `name`
- `account_type` (`Savings` or `Current`)
- `date_of_birth` (DD/MM/YYYY)
- `mobile`
- `gender`
- `nationality`
- `kyc_document`

**transactions**
- `account_number`
- `amount`
- `tx_type` (`deposit` or `withdraw`)
- `balance_after`
- `created_at`

---

## Requirements

- Python 3.10+ (3.11 recommended)
- Tkinter (bundled with most Python installs on Windows/macOS)

Install runtime dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

---

## Run the App

From the repo root:

```bash
python mainProject.py
```

You can also run:

```bash
python -m bank_app
```

---

## First-Time Admin Setup

If no admin exists, the Admin Login screen shows a **Create First Admin** button.

You can also bootstrap via environment variables (optional):

- `BANKAPP_BOOTSTRAP_ADMIN_ID`
- `BANKAPP_BOOTSTRAP_ADMIN_PASSWORD`

Example (PowerShell):

```bash
$env:BANKAPP_BOOTSTRAP_ADMIN_ID="admin"
$env:BANKAPP_BOOTSTRAP_ADMIN_PASSWORD="admin@123"
python mainProject.py
```

After the first admin is created, normal admin login is enabled.

---

## Usage Walkthrough

### Admin
1. Open the app and choose **Employee**
2. Log in as admin
3. Use the menu to:
   - Create admins
   - Create customer accounts
   - View customer summaries
   - Close accounts

### Customer
1. Open the app and choose **Customer**
2. Log in with account number + PIN
3. Use the menu to:
   - Deposit and withdraw money
   - Change PIN
   - Check balance
   - Close account

---

## Business Rules

- **PIN must be exactly 4 digits**
- **Passwords must be at least 6 characters**
- **Minimum balance**: `10000`
- **Max deposit/withdraw per transaction**: `25000`
- **Date format**: `DD/MM/YYYY`

These rules are enforced in `bank_app/services.py` and `bank_app/validation.py`.

---

## Tests

Install dev dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the test suite:

```bash
pytest -q
```

Tests cover:
- Argon2id hashing and verification
- Validation rules (dates, mobile numbers)
- Core service workflows (admin/customer, deposit/withdraw)

---

## CI (GitHub Actions)

A workflow is included at `.github/workflows/python-ci.yml` to run tests on pushes and pull requests.

---

## Legacy Data Migration (Optional)

Older versions stored data in flat text files under `database/`. Those files are now **deprecated** and not used by the app.

If you need to import legacy data into SQLite:

```bash
python scripts/migrate_legacy.py
```

The script reads:
- `database/Admin/adminDatabase.txt`
- `database/Customer/customerDatabase.txt`

---

## Project Structure

```
bank_app/
  config.py
  errors.py
  security.py
  services.py
  storage.py
  ui.py
scripts/
  migrate_legacy.py
tests/
  test_security.py
  test_services.py
  test_validation.py
images/
mainProject.py
README.md
```

---

## Notes for Contributors

- Keep UI code in `bank_app/ui.py` and business logic in `bank_app/services.py`.
- Always validate inputs in the service layer.
- Avoid storing secrets in plaintext.
- If you add new features, add at least one test.

---

## Troubleshooting

**App opens but icons are missing**
- Make sure you run the app from the repo root so `images/` is discoverable.

**Tkinter is missing**
- On Linux, install `python3-tk` via your package manager.

---

If you want, I can also add a small database viewer or export/report feature next.
