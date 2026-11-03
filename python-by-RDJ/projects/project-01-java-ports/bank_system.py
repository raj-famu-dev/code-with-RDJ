# Tags: #Python #Project #JavaToPython #BankSystem | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Bank system: a Python port of project-03 (accounts, custom exceptions, atomic transfers).

Money is stored as whole cents in an int (never float). Account balances are
read-only properties; they change only through deposit/withdraw/transfer.
The core has no input(); the menu is in run()/main().
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum


# ===== SECTION 1: exceptions =====
class BankError(Exception):
    """Base class: catch this to handle any banking failure."""


class InsufficientFundsError(BankError):
    def __init__(self, shortfall_cents: int) -> None:
        self.shortfall_cents = shortfall_cents
        super().__init__(f"Insufficient funds: short by {format_money(shortfall_cents)}.")


class AccountNotFoundError(BankError):
    def __init__(self, account_number: str) -> None:
        self.account_number = account_number
        super().__init__(f"No account with number {account_number!r}.")


class InvalidAmountError(BankError):
    """Zero, negative, wrongly typed or non-cent amounts."""


class InvalidTransferError(BankError):
    """E.g. transferring to the same account."""


# ===== SECTION 2: money helpers =====
def format_money(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    return f"{sign}${abs(cents) // 100:,}.{abs(cents) % 100:02d}"


_AMOUNT_RE = re.compile(r"\d+(\.\d{1,2})?", re.ASCII)


def parse_amount(text: str) -> int:
    """'12.5' -> 1250 cents. Rejects negatives, zero, 3+ decimals and junk (Decimal, never float)."""
    text = text.strip().lstrip("$")
    if not _AMOUNT_RE.fullmatch(text):
        raise InvalidAmountError(f"{text!r} is not a valid amount (use e.g. 12.50).")
    try:
        cents = int(Decimal(text) * 100)
    except InvalidOperation:  # pragma: no cover - regex already guards this
        raise InvalidAmountError(f"{text!r} is not a valid amount.") from None
    if cents <= 0:
        raise InvalidAmountError("Amount must be greater than zero.")
    return cents


def _require_positive_cents(amount_cents: int) -> None:
    if isinstance(amount_cents, bool) or not isinstance(amount_cents, int):
        raise InvalidAmountError("Amount must be a whole number of cents.")
    if amount_cents <= 0:
        raise InvalidAmountError("Amount must be greater than zero.")


# ===== SECTION 3: transactions, interface, accounts =====
class TxType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    INTEREST = "INTEREST"
    FEE = "FEE"


@dataclass(frozen=True)
class Transaction:
    kind: TxType
    amount_cents: int
    balance_after_cents: int
    timestamp: datetime


class Auditable(ABC):
    """Interface: anything that can describe its own audit trail."""

    @abstractmethod
    def audit_lines(self) -> list[str]: ...


Clock = Callable[[], datetime]


class Account(Auditable, ABC):
    """Abstract account. The balance is a read-only property: no setter exists."""

    def __init__(self, number: str, owner_id: int, clock: Clock = datetime.now) -> None:
        self.number = number
        self.owner_id = owner_id
        self._balance = 0
        self._history: list[Transaction] = []
        self._clock = clock

    @property
    def balance_cents(self) -> int:
        return self._balance

    @property
    def history(self) -> tuple[Transaction, ...]:
        return tuple(self._history)  # a copy: callers cannot edit the ledger

    @abstractmethod
    def available_cents(self) -> int:
        """How much can leave this account right now."""

    @abstractmethod
    def monthly_processing(self) -> None:
        """Apply interest and/or fees (each subclass decides)."""

    def _record(self, kind: TxType, amount: int) -> None:
        self._history.append(Transaction(kind, amount, self._balance, self._clock()))

    def _apply(self, delta: int, kind: TxType) -> None:
        self._balance += delta
        self._record(kind, abs(delta))

    def deposit(self, amount_cents: int) -> None:
        _require_positive_cents(amount_cents)
        self._apply(amount_cents, TxType.DEPOSIT)

    def check_can_withdraw(self, amount_cents: int) -> None:
        """Raises if a withdrawal of this size is not allowed. Changes nothing."""
        _require_positive_cents(amount_cents)
        if amount_cents > self.available_cents():
            raise InsufficientFundsError(amount_cents - self.available_cents())

    def withdraw(self, amount_cents: int) -> None:
        self.check_can_withdraw(amount_cents)
        self._apply(-amount_cents, TxType.WITHDRAWAL)

    def audit_lines(self) -> list[str]:
        return [f"{t.timestamp:%Y-%m-%d %H:%M:%S} {t.kind.value:<12} {format_money(t.amount_cents):>12} "
                f"balance {format_money(t.balance_after_cents)}" for t in self._history]

    # Equality by account number: two objects for the same account are the same account.
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Account) and self.number == other.number

    def __hash__(self) -> int:
        return hash(self.number)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.number}, {format_money(self._balance)})"


class SavingsAccount(Account):
    """No overdraft. Earns annual_rate_bp basis points per year (100 bp = 1%), paid monthly."""

    def __init__(self, number: str, owner_id: int, annual_rate_bp: int, clock: Clock = datetime.now) -> None:
        super().__init__(number, owner_id, clock)
        if annual_rate_bp < 0:
            raise ValueError("Rate cannot be negative.")
        self.annual_rate_bp = annual_rate_bp

    def available_cents(self) -> int:
        return self._balance

    def monthly_processing(self) -> None:
        denominator = 12 * 10_000
        interest = (self._balance * self.annual_rate_bp * 2 + denominator) // (2 * denominator)  # round half up
        if interest > 0:
            self._apply(interest, TxType.INTEREST)


class CheckingAccount(Account):
    """Can go down to -overdraft_limit. Charges a flat monthly fee."""

    def __init__(self, number: str, owner_id: int, overdraft_limit_cents: int = 0,
                 monthly_fee_cents: int = 500, clock: Clock = datetime.now) -> None:
        super().__init__(number, owner_id, clock)
        if overdraft_limit_cents < 0 or monthly_fee_cents < 0:
            raise ValueError("Overdraft limit and fee cannot be negative.")
        self.overdraft_limit_cents = overdraft_limit_cents
        self.monthly_fee_cents = monthly_fee_cents

    def available_cents(self) -> int:
        return self._balance + self.overdraft_limit_cents

    def monthly_processing(self) -> None:
        if self.monthly_fee_cents > 0:  # a fee may push the balance past the overdraft limit
            self._apply(-self.monthly_fee_cents, TxType.FEE)


# ===== SECTION 4: customer and bank =====
@dataclass
class Customer:
    customer_id: int
    name: str
    accounts: list[Account] = field(default_factory=list)


class Bank:
    def __init__(self, clock: Clock = datetime.now) -> None:
        self._clock = clock
        self._customers: dict[int, Customer] = {}
        self._accounts: dict[str, Account] = {}
        self._next_customer = 1
        self._next_account = 1

    def add_customer(self, name: str) -> Customer:
        name = name.strip()
        if not name:
            raise ValueError("Customer name cannot be blank.")
        customer = Customer(self._next_customer, name)
        self._customers[customer.customer_id] = customer
        self._next_customer += 1
        return customer

    def get_customer(self, customer_id: int) -> Customer:
        try:
            return self._customers[customer_id]
        except KeyError:
            raise BankError(f"No customer with id {customer_id}.") from None

    def _new_number(self) -> str:
        number = f"ACC-{self._next_account:04d}"
        self._next_account += 1
        return number

    def _register(self, customer: Customer, account: Account) -> Account:
        self._accounts[account.number] = account
        customer.accounts.append(account)
        return account

    def open_savings(self, customer_id: int, annual_rate_bp: int = 200) -> SavingsAccount:
        customer = self.get_customer(customer_id)
        acct = SavingsAccount(self._new_number(), customer_id, annual_rate_bp, self._clock)
        return self._register(customer, acct)  # type: ignore[return-value]

    def open_checking(self, customer_id: int, overdraft_limit_cents: int = 0,
                      monthly_fee_cents: int = 500) -> CheckingAccount:
        customer = self.get_customer(customer_id)
        acct = CheckingAccount(self._new_number(), customer_id, overdraft_limit_cents,
                               monthly_fee_cents, self._clock)
        return self._register(customer, acct)  # type: ignore[return-value]

    def find_account(self, number: str) -> Account:
        try:
            return self._accounts[number.strip().upper()]
        except KeyError:
            raise AccountNotFoundError(number.strip()) from None

    def accounts_of(self, customer_id: int) -> list[Account]:
        return list(self.get_customer(customer_id).accounts)

    def deposit(self, number: str, amount_cents: int) -> None:
        self.find_account(number).deposit(amount_cents)

    def withdraw(self, number: str, amount_cents: int) -> None:
        self.find_account(number).withdraw(amount_cents)

    def transfer(self, from_number: str, to_number: str, amount_cents: int) -> None:
        """All or nothing. Every check runs BEFORE any balance changes; a rollback guards the rest."""
        src = self.find_account(from_number)
        dst = self.find_account(to_number)
        if src is dst:
            raise InvalidTransferError("Cannot transfer to the same account.")
        src.check_can_withdraw(amount_cents)  # amount, funds: may raise, mutates nothing
        snapshot = [(a, a._balance, len(a._history)) for a in (src, dst)]
        try:
            src._apply(-amount_cents, TxType.TRANSFER_OUT)
            dst._apply(amount_cents, TxType.TRANSFER_IN)
        except Exception:
            for acct, balance, hist_len in snapshot:  # restore both sides, then re-raise
                acct._balance = balance
                del acct._history[hist_len:]
            raise

    def run_monthly_processing(self) -> None:
        for account in self._accounts.values():
            account.monthly_processing()  # polymorphic: interest, fee, ...

    def total_balance_cents(self) -> int:
        return sum(a.balance_cents for a in self._accounts.values())


# ===== SECTION 5: demo that triggers every custom exception on purpose =====
def demo(write: Callable[[str], None] = print) -> None:
    fixed = datetime(2026, 1, 1, 12, 0, 0)
    bank = Bank(clock=lambda: fixed)
    ada = bank.add_customer("Ada")
    sav = bank.open_savings(ada.customer_id, 1200)
    chk = bank.open_checking(ada.customer_id, overdraft_limit_cents=5000)
    bank.deposit(sav.number, 100_000)
    attempts: list[tuple[str, Callable[[], None]]] = [
        ("withdraw 2000.00 from savings", lambda: bank.withdraw(sav.number, 200_000)),
        ("deposit -5.00", lambda: bank.deposit(sav.number, -500)),
        ("parse amount '12.345'", lambda: parse_amount("12.345")),
        ("deposit to ACC-9999", lambda: bank.deposit("ACC-9999", 100)),
        ("transfer savings -> savings", lambda: bank.transfer(sav.number, sav.number, 100)),
        ("transfer 5000.00 savings -> checking", lambda: bank.transfer(sav.number, chk.number, 500_000)),
    ]
    before = bank.total_balance_cents()
    for label, action in attempts:
        try:
            action()
        except BankError as err:
            write(f"{type(err).__name__:<24} <- {label}: {err}")
    write(f"Total balance unchanged by failures: {bank.total_balance_cents() == before}")


# ===== SECTION 6: interactive layer =====
Reader = Callable[[str], str]
Writer = Callable[[str], None]

MENU = """\
===== BANK =====
1. New customer          2. Open savings account    3. Open checking account
4. Deposit               5. Withdraw                6. Transfer
7. Account statement     8. Accounts of a customer  9. Run monthly processing
10. Run exceptions demo  0. Exit"""


def _read_int(read: Reader, prompt: str) -> int:
    text = read(prompt).strip()
    if not (text.isascii() and text.isdigit()):
        raise BankError("Please enter a whole number.")
    return int(text)


def run(read: Reader = input, write: Writer = print, bank: Bank | None = None) -> Bank:
    bank = bank if bank is not None else Bank()
    while True:
        write(MENU)
        choice = read("Choose an option: ").strip()
        try:
            if choice == "0":
                write("Goodbye!")
                return bank
            elif choice == "1":
                c = bank.add_customer(read("Customer name: "))
                write(f"Customer {c.customer_id} created: {c.name}")
            elif choice == "2":
                cid = _read_int(read, "Customer id: ")
                # "2.5" percent parses like "2.50 dollars" -> 250, which is exactly 250 basis points
                rate_bp = parse_amount(read("Annual rate in percent (e.g. 2.5): "))
                a = bank.open_savings(cid, rate_bp)
                write(f"Opened {a.number} (savings, {a.annual_rate_bp} bp)")
            elif choice == "3":
                cid = _read_int(read, "Customer id: ")
                limit_text = read("Overdraft limit (blank = 0): ").strip()
                limit = parse_amount(limit_text) if limit_text else 0
                a = bank.open_checking(cid, limit)
                write(f"Opened {a.number} (checking, overdraft {format_money(limit)})")
            elif choice in ("4", "5"):
                number = read("Account number: ")
                cents = parse_amount(read("Amount: "))
                if choice == "4":
                    bank.deposit(number, cents)
                    write(f"Deposited {format_money(cents)}.")
                else:
                    bank.withdraw(number, cents)
                    write(f"Withdrew {format_money(cents)}.")
                write(f"New balance: {format_money(bank.find_account(number).balance_cents)}")
            elif choice == "6":
                src = read("From account: ")
                dst = read("To account: ")
                cents = parse_amount(read("Amount: "))
                bank.transfer(src, dst, cents)
                write(f"Transferred {format_money(cents)}.")
            elif choice == "7":
                acct = bank.find_account(read("Account number: "))
                write(f"{acct!r}")
                for line in acct.audit_lines() or ["(no transactions)"]:
                    write(line)
            elif choice == "8":
                owned = bank.accounts_of(_read_int(read, "Customer id: "))
                for acct in owned:
                    write(repr(acct))
                if not owned:
                    write("(no accounts)")
            elif choice == "9":
                bank.run_monthly_processing()
                write("Monthly processing done.")
            elif choice == "10":
                demo(write)
            else:
                write("Invalid option.")
        except (BankError, ValueError) as err:
            write(f"Error: {err}")
        write("")


def main() -> None:
    try:
        run()
    except EOFError:
        print("\nInput ended. Goodbye!")


if __name__ == "__main__":
    main()
