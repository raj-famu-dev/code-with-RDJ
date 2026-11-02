# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""pytest tests for bank_system.py."""
import random
from datetime import datetime, timedelta

import pytest

import bank_system as bs


def make_io(lines):
    it = iter(lines)
    out: list[str] = []
    return (lambda prompt: next(it)), out.append, out


class FakeClock:
    def __init__(self):
        self.now = datetime(2026, 1, 1)

    def __call__(self):
        self.now += timedelta(seconds=1)
        return self.now


@pytest.fixture
def bank():
    b = bs.Bank(FakeClock())
    ada = b.add_customer("Ada")
    b.open_savings(ada.customer_id, 1200)                         # ACC-0001, 12% a year
    b.open_checking(ada.customer_id, overdraft_limit_cents=5000)  # ACC-0002
    b.deposit("ACC-0001", 100_000)
    b.deposit("ACC-0002", 10_000)
    return b


@pytest.mark.parametrize("text,cents", [("12.5", 1250), ("$0.01", 1), ("100", 10000), (" 3.50 ", 350)])
def test_parse_amount_ok(text, cents):
    assert bs.parse_amount(text) == cents


@pytest.mark.parametrize("text", ["0", "0.00", "-5", "1.234", "abc", "", "1e3", "1,000", "nan", "٣"])
def test_parse_amount_rejects(text):
    with pytest.raises(bs.InvalidAmountError):
        bs.parse_amount(text)


def test_float_trap_avoided():
    assert 0.1 + 0.2 != 0.3
    assert bs.parse_amount("0.10") + bs.parse_amount("0.20") == bs.parse_amount("0.30")


@pytest.mark.parametrize("cents,text", [(0, "$0.00"), (5, "$0.05"), (123456, "$1,234.56"), (-250, "-$2.50")])
def test_format_money(cents, text):
    assert bs.format_money(cents) == text


@pytest.mark.parametrize("bad", [0, -1, 1.5, "5", True, None])
def test_invalid_amounts_raise(bank, bad):
    with pytest.raises(bs.InvalidAmountError):
        bank.deposit("ACC-0001", bad)
    with pytest.raises(bs.InvalidAmountError):
        bank.withdraw("ACC-0001", bad)
    assert bank.find_account("ACC-0001").balance_cents == 100_000


def test_balance_has_no_setter(bank):
    acct = bank.find_account("ACC-0001")
    with pytest.raises(AttributeError):
        acct.balance_cents = 1
    with pytest.raises(AttributeError):
        acct.history.append(None)  # history is a tuple copy


def test_savings_cannot_overdraw_and_shortfall_is_exact(bank):
    with pytest.raises(bs.InsufficientFundsError) as exc:
        bank.withdraw("ACC-0001", 100_001)
    assert exc.value.shortfall_cents == 1
    assert bank.find_account("ACC-0001").balance_cents == 100_000


def test_checking_overdraft_limit_boundary(bank):
    bank.withdraw("ACC-0002", 15_000)  # 10,000 + 5,000 overdraft: exactly the limit
    assert bank.find_account("ACC-0002").balance_cents == -5_000
    with pytest.raises(bs.InsufficientFundsError) as exc:
        bank.withdraw("ACC-0002", 1)
    assert exc.value.shortfall_cents == 1


def test_unknown_account(bank):
    with pytest.raises(bs.AccountNotFoundError) as exc:
        bank.deposit("ACC-9999", 100)
    assert exc.value.account_number == "ACC-9999"
    assert bank.find_account(" acc-0001 ").number == "ACC-0001"  # lookup trims and ignores case


def test_all_errors_share_base_class():
    for cls in (bs.InsufficientFundsError, bs.AccountNotFoundError,
                bs.InvalidAmountError, bs.InvalidTransferError):
        assert issubclass(cls, bs.BankError)


def test_transfer_success_moves_money_and_keeps_total(bank):
    before = bank.total_balance_cents()
    bank.transfer("ACC-0001", "ACC-0002", 25_000)
    assert bank.find_account("ACC-0001").balance_cents == 75_000
    assert bank.find_account("ACC-0002").balance_cents == 35_000
    assert bank.total_balance_cents() == before
    kinds = [t.kind for t in bank.find_account("ACC-0001").history]
    assert kinds[-1] is bs.TxType.TRANSFER_OUT
    assert bank.find_account("ACC-0002").history[-1].kind is bs.TxType.TRANSFER_IN


@pytest.mark.parametrize("src,dst,amount,exc", [
    ("ACC-0001", "ACC-0002", 999_999_999, bs.InsufficientFundsError),
    ("ACC-0001", "ACC-0002", 0, bs.InvalidAmountError),
    ("ACC-0001", "ACC-0002", -5, bs.InvalidAmountError),
    ("ACC-0001", "ACC-9999", 100, bs.AccountNotFoundError),
    ("ACC-9999", "ACC-0002", 100, bs.AccountNotFoundError),
    ("ACC-0001", "ACC-0001", 100, bs.InvalidTransferError),
])
def test_failed_transfer_changes_nothing(bank, src, dst, amount, exc):
    snapshot = {n: (a.balance_cents, len(a.history)) for n, a in bank._accounts.items()}
    with pytest.raises(exc):
        bank.transfer(src, dst, amount)
    assert {n: (a.balance_cents, len(a.history)) for n, a in bank._accounts.items()} == snapshot


def test_transfer_rolls_back_if_second_leg_blows_up(bank, monkeypatch):
    dst = bank.find_account("ACC-0002")

    def boom(delta, kind):
        raise RuntimeError("disk full")

    monkeypatch.setattr(dst, "_apply", boom)
    with pytest.raises(RuntimeError):
        bank.transfer("ACC-0001", "ACC-0002", 500)
    assert bank.find_account("ACC-0001").balance_cents == 100_000
    assert len(bank.find_account("ACC-0001").history) == 1
    assert dst.balance_cents == 10_000


def test_total_balance_invariant_under_random_transfers(bank):
    rng = random.Random(42)
    bank.open_savings(1, 100)  # ACC-0003
    total = bank.total_balance_cents()
    names = ["ACC-0001", "ACC-0002", "ACC-0003"]
    for _ in range(300):
        a, b = rng.sample(names, 2)
        try:
            bank.transfer(a, b, rng.randint(-100, 60_000))
        except bs.BankError:
            pass
        assert bank.total_balance_cents() == total


def test_history_records_type_amount_balance_after_timestamp(bank):
    h = bank.find_account("ACC-0001").history[0]
    assert (h.kind, h.amount_cents, h.balance_after_cents) == (bs.TxType.DEPOSIT, 100_000, 100_000)
    assert isinstance(h.timestamp, datetime)
    bank.withdraw("ACC-0001", 1)
    h2 = bank.find_account("ACC-0001").history[-1]
    assert h2.balance_after_cents == 99_999 and h2.timestamp > h.timestamp


def test_monthly_processing_is_polymorphic(bank):
    bank.run_monthly_processing()
    # 1% a month on 1,000.00 = 10.00 interest; checking pays the 5.00 fee
    assert bank.find_account("ACC-0001").balance_cents == 101_000
    assert bank.find_account("ACC-0001").history[-1].kind is bs.TxType.INTEREST
    assert bank.find_account("ACC-0002").balance_cents == 9_500
    assert bank.find_account("ACC-0002").history[-1].kind is bs.TxType.FEE


def test_interest_rounds_half_up_and_zero_balance_records_nothing():
    b = bs.Bank()
    c = b.add_customer("X")
    s = b.open_savings(c.customer_id, 1200)
    b.run_monthly_processing()
    assert s.history == ()
    b.deposit(s.number, 50)  # 1% of 50 cents = 0.5 -> rounds to 1
    b.run_monthly_processing()
    assert s.balance_cents == 51


def test_abstract_account_cannot_be_instantiated():
    with pytest.raises(TypeError):
        bs.Account("X", 1)


def test_accounts_implement_auditable_interface(bank):
    acct = bank.find_account("ACC-0001")
    assert isinstance(acct, bs.Auditable) and len(acct.audit_lines()) == 1


def test_lookup_and_customer_with_several_accounts(bank):
    assert [a.number for a in bank.accounts_of(1)] == ["ACC-0001", "ACC-0002"]
    with pytest.raises(bs.BankError):
        bank.accounts_of(77)
    with pytest.raises(ValueError):
        bank.add_customer("  ")


def test_account_equality_and_hash_by_number():
    a = bs.SavingsAccount("ACC-1", 1, 100)
    b = bs.CheckingAccount("ACC-1", 2)
    assert a == b and len({a, b}) == 1


def test_demo_triggers_every_exception_type():
    out: list[str] = []
    bs.demo(out.append)
    text = "\n".join(out)
    for name in ("InsufficientFundsError", "InvalidAmountError", "AccountNotFoundError", "InvalidTransferError"):
        assert name in text
    assert "unchanged by failures: True" in text


def test_cli_flow():
    read, write, out = make_io([
        "1", "Ada", "2", "1", "2.5", "3", "1", "50", "4", "ACC-0001", "100.00",
        "6", "ACC-0001", "ACC-0002", "30", "5", "ACC-0002", "99", "4", "ACC-0001", "-5",
        "4", "ACC-0001", "abc", "6", "ACC-0001", "ACC-0009", "1", "9", "7", "ACC-0001",
        "8", "1", "8", "x", "x", "0"])
    bank = bs.run(read, write)
    text = "\n".join(out)
    assert "Customer 1 created: Ada" in text and "(savings, 250 bp)" in text
    assert "Deposited $100.00." in text and "Transferred $30.00." in text
    assert "Insufficient funds: short by $19.00." in text
    assert text.count("not a valid amount") == 2 and "No account with number 'ACC-0009'" in text
    assert "Monthly processing done." in text and "Invalid option." in text
    assert "Please enter a whole number." in text
    # 70.00 at 2.5%/12 = 0.1458... -> 0.15 interest; checking 30.00 - 5.00 fee = 25.00
    assert bank.find_account("ACC-0001").balance_cents == 7_015
    assert bank.find_account("ACC-0002").balance_cents == 2_500
    assert "INTEREST" in text
