> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Adapter

## Concept

**Problem:** your code expects interface A; a legacy or third-party class (which you cannot or should not edit) offers the same capability through interface B. **Solution:** a small class that **implements A** and internally **calls B**, like a travel plug adapter. **Trade-off:** one more layer that can hide a poor fit (units, error handling, performance); if you can change the original class, change it instead.

## Full Line-by-Line Breakdown

**The target.** `PaymentGateway.charge(String customerId, double dollars)` returns `boolean`. `InHousePayments` already fits.

**The adaptee.** `LegacyBillingSystem.makePayment(long accountNumber, long amountInCents)` returns an `int` status code (0 = OK, 2 = limit exceeded). Different types, units and result style.

**The adapter.** `LegacyBillingAdapter implements PaymentGateway` and **has** a `LegacyBillingSystem` (composition). It translates:
- id: `"C-1042"` becomes `1042`
- amount: dollars become cents with `Math.round(dollars * 100)`
- result: code `0` becomes `true`

**Using it.** `CheckoutService` depends only on `PaymentGateway` and is never touched:

```
  legacy: account 1042 debited 1999 cents
legacy result:   paid
  legacy: account 1042 debited 150000 cents
legacy over its limit: payment failed
```

**The rounding trap.** `19.99 * 100` is `1998.9999999999998` in binary floating point, so truncating gives `1998` cents; rounding gives `1999`. (Real systems keep money in cents or `BigDecimal` from the start.)

**JDK examples.** `Arrays.asList(array)` adapts an array to `List`; `InputStreamReader` adapts bytes to characters.

## Key Rules

1. The adapter implements the interface your code wants.
2. It holds the foreign object and delegates, translating on the way.
3. Round money deliberately; never truncate by accident.
4. Keep the adapter thin: translation only, no business rules.

## Gotchas Recap

- A `false` that hides five different legacy error codes loses information.
- Units (dollars vs cents) are the usual bug source.
- Adapters stacked on adapters become impossible to trace.

## Why This Structure Exists

The two incompatible interfaces are shown side by side first, so the adapter's three translations are obvious. Exit test: adapting a class you own and could simply fix adds a layer for nothing.
