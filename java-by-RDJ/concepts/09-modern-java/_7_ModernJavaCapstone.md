> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Modern Java Capstone: Payment System

## Concept

A small payment processor that uses the folder's features together: sealed interfaces, records with validation, pattern `switch` (exhaustive, no `default`), record patterns, `java.time`, text blocks and `var`. Money uses `BigDecimal`, never `double`, because binary floating point cannot represent values like 0.10 exactly.

## Full Line-by-Line Breakdown

**The model.**
- `sealed interface PaymentMethod permits Card, BankTransfer, Wallet`, each a record with a validating compact constructor (`last4` must be 4 digits, IBAN length, non-null fields).
- `Payment` normalizes the amount to 2 decimals with `setScale(2, HALF_UP)` and rejects zero/negative.
- `sealed interface Outcome permits Approved, Declined`.

**`fee(payment)`.** A switch over the sealed `PaymentMethod`: card 2.9% + 0.30, bank transfer flat 0.50, wallet 1.5%. No `default`: adding a method breaks compilation until handled.

**`process(payment, today)`.** A pattern switch with record patterns and guards, checked in order:
1. a card whose `expires` is before this month: declined;
2. an unverified wallet: declined;
3. a bank transfer over 10,000: declined;
4. anything else: `case PaymentMethod m` approves with a computed fee.

The date is fixed (`2026-03-01`) so output never changes.

**Output.**

```
APPROVED P1   100.00 via card ****4242          fee 3.20
APPROVED P2   250.50 via bank transfer DE89...  fee 0.50
APPROVED P3    40.00 via PayPal wallet          fee 0.60
DECLINED P4    75.00 via card ****1111          -> card ending 1111 expired 2025-12
DECLINED P5    20.00 via QuickPay wallet        -> QuickPay wallet is not verified
DECLINED P6 12000.00 via bank transfer GB29...  -> bank transfers are limited to 10,000.00
outcomes: {Approved=3, Declined=3}, total fees collected: 4.30
```

(Check P1: 100.00 x 0.029 + 0.30 = 3.20. P3: 40.00 x 0.015 = 0.60.)

**Report.** A text block with `formatted(...)`. **Validation** at construction rejects a negative amount and a card with letters in `last4`.

**Exit-test notes (in the file).** Boilerplate replaced: records (each would be about 25 lines of fields, constructor, getters, `equals`, `hashCode`, `toString`) and sealed + switch (replaces an if/else chain and adds compile-time exhaustiveness). Showing off: the catch-all `case PaymentMethod m` after guards is clever but harder for a newcomer than a plain if-chain; `var` on every line would hurt.

## Key Rules

1. Model "one of these exact cases" as sealed types plus records.
2. Validate in compact constructors so invalid objects cannot exist.
3. Money is `BigDecimal` with an explicit scale and rounding mode.
4. Order guarded cases before the catch-all.

## Gotchas Recap

- `new BigDecimal(0.1)` (from a double) is not 0.1: use strings.
- Fees are rounded after calculation (`HALF_UP` to 2 decimals).
- A pattern switch's catch-all can hide that a rule was never added.

## Why This Structure Exists

Each feature does a job a reader can name, and the final notes make you argue where each one earns its place.
