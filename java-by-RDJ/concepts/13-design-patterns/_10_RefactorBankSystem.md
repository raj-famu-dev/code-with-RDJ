> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Refactor a Bank System (Strategy + Observer)

## Concept

**Problem:** a small bank where one class decides fees by if/else on account type **and** prints receipts **and** "emails" a manager. **Solution:** apply **Strategy** for fees and **Observer** for reactions. **Trade-off:** more types and indirection; for two account types and one print line the original would have been fine.

> Honest note: `projects/project-03-bank-system` is only a specification so far. This file is a **miniature** bank with the same ideas (account types, fees, history). When you build project-03, repeat this refactor on **your** code. Money is whole cents in a `long`, never `double`.

## Full Line-by-Line Breakdown

**BEFORE: `BadAccount`.**
- `monthlyFee()` is an if/else on a `type` string: a new type means editing the method.
- `withdraw` prints a receipt and "emails the manager" itself: presentation and notification inside the account.

```
  [bad] receipt printed: withdrew 1200.00
  [bad] emailing manager: large withdrawal
  new account type unsupported until the class is edited: unknown type student
```

**AFTER, pattern 1: Strategy.** `FeePolicy` is a functional interface (`monthlyFee(balanceCents)`): `CHECKING_FEE` (12.00 below 500.00), `NO_FEE`, `PREMIUM_FEE`. `Account` receives one. A **new** student account needs one lambda (`balance -> 300`), with no class edited.

**AFTER, pattern 2: Observer.** `Account` publishes a `TransactionEvent` after each change. `ReceiptPrinter`, `LargeWithdrawalAlert` and `StatementHistory` are separate listeners added without touching `Account`. It now has one job: a correct balance. A checked `InsufficientFundsException` carries the shortfall:

```
  receipt: WITHDRAW 1200.00 on CHK-1, balance 1300.00
  receipt: DEPOSIT 500.00 on PRM-1, balance 9500.00
  rejected: short by 500.00 (shortfall cents = 50000)
  receipt: FEE 25.00 on PRM-1, balance 9475.00
  receipt: FEE 3.00 on STU-1, balance 397.00
  alerts: [large withdrawal of 1200.00 on CHK-1]
  history entries recorded: 4
```

**Equivalence check.** The Strategy gives the same fees as the old if/else for four test balances (`true`) and for premium (`true`). Always verify a refactor changed the structure, not the behaviour.

**Before/after, honestly.** Wins: a new account kind and a new reaction each needed no edits to `Account`; `Account` is testable alone. Costs: longer code, more types, and a reader must discover which listeners and policy an account was given.

## Key Rules

1. Refactor with a check that behaviour did not change.
2. Strategy for "which algorithm", Observer for "who reacts".
3. Keep the core class to one job.
4. Money in cents or `BigDecimal`.

## Gotchas Recap

- Listener exceptions: this version does not protect the loop (see `_8` for how).
- Observer and Strategy do not give you transactions: a transfer between two accounts needs its own atomicity (project-03 asks for it).
- Refactoring without tests is a guess.

## Why This Structure Exists

BEFORE and AFTER in one file, with the same scenario run through both, make the patterns something you measure, not admire.
