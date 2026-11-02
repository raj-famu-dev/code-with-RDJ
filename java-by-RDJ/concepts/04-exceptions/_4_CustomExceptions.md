# `_4_CustomExceptions.java`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A custom exception is your own class that extends `Exception` (checked) or `RuntimeException` (unchecked). It says exactly **what** went wrong and can carry data a handler needs.

## Full Line-by-Line Breakdown

### The exception hierarchy
```
BankException (extends Exception, checked)
  InsufficientFundsException    carries a shortfall amount
  AccountLockedException
InvalidAmountException (extends RuntimeException, unchecked)
```
- `BankException` is a shared parent so callers can catch "any banking problem" in one `catch`.
- `InsufficientFundsException` stores `shortfall` and exposes `getShortfall()`, so a handler can say "you are short by X".
- Each constructor passes a message to `super(message)`.

### The `Account` class
`withdraw(double)` declares `throws BankException` and checks, in order: non-positive amount (`InvalidAmountException`), locked account (`AccountLockedException`), amount over balance (`InsufficientFundsException`). Otherwise it subtracts.

### SECTION 1: Why make your own
`IllegalArgumentException` says "something was wrong". `InsufficientFundsException` says **what**, and can carry data. Withdrawing 150 from 100: `Caught: Insufficient funds, short by 50.0 (shortfall field = 50.0)`.

### SECTION 2: A hierarchy lets callers pick their precision
Catching `BankException` handles any subtype. For the locked account, the output shows the actual class: `Caught via parent type: Account ACC-2 is locked [AccountLockedException]`.

### SECTION 3: Checked or unchecked?
- Extend `Exception`: the caller **must** handle it. Use when a reasonable caller can recover.
- Extend `RuntimeException`: not forced. Use for programming errors.
Insufficient funds and locked accounts are normal business outcomes (checked); a negative amount is a bug (unchecked). Output: `Caught unchecked: Amount must be positive but was -20.0`.

### SECTION 4: A successful call
`withdraw(30)` works: `Withdrew 30, balance now 70.0`.

### SECTION 5: Design tips
End names with `Exception`; give the constructor a message (and a cause, see `_6`); add fields only for data a handler will use; do not create a type per error, only when a caller would handle it differently.

## Key Rules / Gotchas Recap
- Catch order: specific subclasses before the parent (the code does this)
- Checked = caller can recover; unchecked = caller made a mistake
- Money as `double` is used here only to keep the demo short; `project-03` asks for `BigDecimal` or whole cents

## Why This Structure Exists
Generic exceptions make callers parse message text to decide what to do. Named types plus data let code react precisely, and they document the failure modes of a method right in its signature.
