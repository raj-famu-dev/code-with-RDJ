# `bank_system.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A small banking model: customers own several accounts, an abstract `Account` has `SavingsAccount` (interest) and `CheckingAccount` (overdraft limit and monthly fee) subclasses, and every deposit, withdrawal and transfer is recorded as a transaction. Failures are reported with a custom exception hierarchy, and a transfer is all-or-nothing: if it fails for any reason, both balances (and both histories) are exactly as they were. Money is stored as whole cents in an `int`, never as a `float`.

## Full Line-by-Line Breakdown

### SECTION 1: exceptions
- `BankError(Exception)` is the base so callers can catch any banking failure at once.
- `InsufficientFundsError` carries `shortfall_cents` (an attribute set in `__init__`, then `super().__init__(message)`). `AccountNotFoundError` carries the number. `InvalidAmountError` covers zero, negative, wrong type and malformed amounts. `InvalidTransferError` (an extra, for transferring to the same account) is also a `BankError`.
- Names follow Python's `...Error` convention rather than Java's `...Exception`. Checked vs unchecked (the spec asks to defend the choice): Python has no checked exceptions, so all of these behave like Java's unchecked ones; nothing forces a caller to handle them, so tests and the demo are what prove each path.

### SECTION 2: money helpers
- Why not `float`: `0.1 + 0.2 != 0.3` in binary floating point, so cents would drift. A test shows `parse_amount("0.10") + parse_amount("0.20") == parse_amount("0.30")` using ints.
- `format_money(cents)` builds `$1,234.56` with integer `//` and `%` (and a leading `-` for negatives).
- `parse_amount("12.5")` uses a regex (digits, optional 1-2 decimals), then `Decimal` times 100 converted to `int`. It rejects `-5`, `0`, `1.234` (sub-cent), `1e3`, `1,000`, `nan`, `abc`.

### SECTION 3: transactions, interface, accounts
- `TxType` enum and a frozen `Transaction` dataclass record type, amount, balance after, and timestamp. The clock is injectable (`Clock = Callable[[], datetime]`), so tests use a fake clock and get deterministic times.
- `Auditable(ABC)` is the interface (Java `interface`): one abstract method `audit_lines`.
- `Account(Auditable, ABC)` is abstract: `available_cents` and `monthly_processing` are `@abstractmethod`, so `Account(...)` itself raises `TypeError` (tested).
- Encapsulation: the balance is `_balance` (a convention: single underscore means "private by agreement") exposed only through a read-only `@property`. There is no setter, so `acct.balance_cents = 1` raises `AttributeError` (tested). `history` returns a tuple copy so callers cannot edit the ledger. Python cannot truly hide attributes; `bank._accounts` and `account._balance` are still reachable, and `Bank.transfer` touches `_balance`/`_history` deliberately because it needs to roll back (same module, "friend" access).
- `deposit` and `withdraw` validate first (`_require_positive_cents` rejects 0, negatives, floats, strings and `True`), then call `_apply`, which changes the balance and records the transaction together.
- `check_can_withdraw` raises `InsufficientFundsError(shortfall)` without changing anything. Savings allows only the balance; checking allows balance + overdraft limit, so `available_cents` is the polymorphic part.
- `SavingsAccount.monthly_processing` pays `annual_rate_bp / 12` of the balance, rounded half-up in integer math (`bp` = basis points, 100 bp = 1%). Zero interest records nothing. `CheckingAccount.monthly_processing` charges the flat fee.
- `__eq__`/`__hash__` use only the account number (the spec's `equals`/`hashCode` question): two objects with the same number are the same account.

### SECTION 4: customer and bank
- `Bank` keeps `dict`s of customers and accounts and counters for ids (`ACC-0001`, ...). `find_account` trims and upper-cases the number and raises `AccountNotFoundError`.
- Validation lives in both places on purpose: the account protects its own invariants (amount positive, funds available), the bank resolves names to accounts and handles things that involve more than one account.
- `transfer` atomicity, without a database: (1) look up both accounts (may raise), (2) reject same account, (3) `src.check_can_withdraw(amount)` validates amount and funds, so every expected failure happens before any mutation, (4) take a snapshot of both balances and history lengths, apply both legs inside `try`, and on any unexpected exception restore both and re-raise. A test forces the second leg to blow up and checks nothing changed.
- `total_balance_cents` sums all accounts. A transfer only moves cents between accounts, so the total is unchanged; a seeded randomized test performs 300 transfers (valid and invalid) and asserts the total never changes.
- `run_monthly_processing` calls `account.monthly_processing()` on every account without checking its type (polymorphism).

### SECTION 5: demo
`demo()` triggers every custom exception on purpose and prints them (output is deterministic; real run, via menu option 10):

```text
InsufficientFundsError   <- withdraw 2000.00 from savings: Insufficient funds: short by $1,000.00.
InvalidAmountError       <- deposit -5.00: Amount must be greater than zero.
InvalidAmountError       <- parse amount '12.345': '12.345' is not a valid amount (use e.g. 12.50).
AccountNotFoundError     <- deposit to ACC-9999: No account with number 'ACC-9999'.
InvalidTransferError     <- transfer savings -> savings: Cannot transfer to the same account.
InsufficientFundsError   <- transfer 5000.00 savings -> checking: Insufficient funds: short by $4,000.00.
Total balance unchanged by failures: True
```

### SECTION 6: interactive layer
Real output of a piped session (menu banner lines removed; exit code 0): create customer, open savings at 2.5%, open checking with $50 overdraft, deposit, transfer, over-withdraw, bad transfers, monthly processing, statement.

```text
Choose an option: Customer name: Customer 1 created: Ada

Choose an option: Customer id: Annual rate in percent (e.g. 2.5): Opened ACC-0001 (savings, 250 bp)

Choose an option: Customer id: Overdraft limit (blank = 0): Opened ACC-0002 (checking, overdraft $50.00)

Choose an option: Account number: Amount: Deposited $100.00.
New balance: $100.00

Choose an option: From account: To account: Amount: Transferred $30.00.

Choose an option: Account number: Amount: Error: Insufficient funds: short by $19.00.

Choose an option: From account: To account: Amount: Error: Cannot transfer to the same account.

Choose an option: Account number: Amount: Error: '-5' is not a valid amount (use e.g. 12.50).

Choose an option: From account: To account: Amount: Error: No account with number 'ACC-0009'.

Choose an option: Monthly processing done.

Choose an option: Account number: SavingsAccount(ACC-0001, $70.15)
2026-11-02 15:02:09 DEPOSIT           $100.00 balance $100.00
2026-11-02 15:02:09 TRANSFER_OUT       $30.00 balance $70.00
2026-11-02 15:02:09 INTEREST            $0.15 balance $70.15
```
The timestamps come from the real clock, so they differ on every run (tests use a fake clock). Interest check: 2.5% / 12 of $70.00 is $0.1458..., rounded half-up to $0.15.

### Requirements self-check
| Requirement | Where |
|---|---|
| Customers with several accounts | `Customer.accounts`, `Bank.accounts_of` |
| Abstract `Account`, Savings, Checking | `Account`, `SavingsAccount`, `CheckingAccount` |
| Deposit, withdraw, transfer | `Account.deposit/withdraw`, `Bank.transfer` |
| History with type, amount, balance after, timestamp | `Transaction` |
| Monthly interest/fees, polymorphic | `run_monthly_processing` |
| Lookup by number / by customer | `find_account`, `accounts_of` |
| Three custom exceptions | `InsufficientFundsError`, `AccountNotFoundError`, `InvalidAmountError` |
| No balance setter | read-only property |
| An interface | `Auditable` |
| Failed transfer leaves both balances unchanged | `Bank.transfer` + tests |
| Money not a `double` | integer cents |
| Demo triggers every exception | `demo()` |

### Bugs I hit
- First draft of the CLI rate prompt multiplied and divided by 100 for no reason; removed. A percent like `2.5` parses with the same code as dollars (`2.50` -> 250), which is exactly 250 basis points.
- My first CLI test expected a balance line that never prints (only deposit/withdraw print one). The test was wrong, not the code; rewritten with exact expected values worked out by hand ($70.15 and $25.00).

## Key Differences From Java

| Java | Python |
|---|---|
| `BigDecimal` or `long` cents | `int` cents (and `Decimal` only for parsing text) |
| `private` fields | `_name` by convention; read-only `@property` for the balance |
| `abstract class` / `interface` | `ABC` + `@abstractmethod` (an interface is just an ABC with only abstract methods) |
| `class InsufficientFundsException extends Exception` (checked) | subclass of `Exception`; no checked exceptions exist |
| `equals`/`hashCode` | `__eq__`/`__hash__` |
| `LocalDateTime.now()` | `datetime.now()` (injected as a clock for testing) |
| `try/finally` rollback | `try/except Exception: restore; raise` |

## Key Rules / Gotchas Recap
- Never store money in `float`; use integer cents.
- Check everything that can fail before mutating anything; keep a rollback only for the unexpected.
- Python has no `private`: expose read-only `@property`, return copies of internal lists.
- A bare `raise` inside `except` re-raises the original error with its traceback.
- Define `__eq__` and `__hash__` together, on fields that never change.
- `True` is an `int` in Python: reject it explicitly when validating amounts.

## Why This Structure Exists
Payments, ledgers and any system that moves value between records need the same properties: exact arithmetic, validated inputs, all-or-nothing updates, and an audit trail. The same ideas show up when an AI agent is allowed to take actions: validate first, apply atomically, log everything.
