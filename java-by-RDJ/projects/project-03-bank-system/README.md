# Project 03 — Bank System

**Status:** ⬜ Not started · **Needs:** `02-oop`, `03-collections`, `04-exceptions`

## 📌 Project Description

A console banking application that combines all four OOP pillars with a real custom exception hierarchy. This is the capstone for `02-oop` and `04-exceptions` together.

## 📋 Requirements

### Functional Requirements
1. **Customers and accounts** — a customer can hold several accounts
2. **Account types** — an abstract `Account` with at least `SavingsAccount` (interest) and `CheckingAccount` (overdraft limit)
3. **Operations** — deposit, withdraw, transfer between accounts
4. **Transaction history** — every operation is recorded with type, amount, balance after, and timestamp
5. **Monthly processing** — apply interest and fees polymorphically across all accounts
6. **Lookup** — find an account by number; find all accounts of a customer

### Custom Exceptions (required)
- `InsufficientFundsException` (checked, carries the shortfall amount)
- `AccountNotFoundException`
- `InvalidAmountException` (negative or zero amounts)
- Decide checked vs unchecked for each and defend the choice in the `.md`

### Non-Functional Requirements
- Account state is private; no setter lets outside code set the balance directly
- At least one `interface` (for example `Auditable` or `InterestBearing`)
- A failed transfer must leave **both** balances unchanged
- Money is not stored as `double`: use `BigDecimal` or whole cents in a `long`, and explain why

## 🔍 Things to Decide and Document
- Where validation lives (account, bank, or both) and why
- What your `equals`/`hashCode` for `Account` is based on
- How the transfer method guarantees atomicity without a database

## ✅ Definition of Done
- [ ] Source files plus a full walkthrough `.md`
- [ ] Requirements-to-code self-check table
- [ ] A demo `main` that triggers every custom exception on purpose
- [ ] A section titled "Bugs I hit"

## 🚀 Possible Extensions
- Persist to a file (`07-file-io`) or database (`10-jdbc-sql`)
- Apply Strategy to fee calculation (`13-design-patterns`)
- Rewrite as a REST API in `project-07`
