> 📘 Reference material drafted with Claude. Not yet learned: retype `_7_Strategy.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Strategy

## Concept

**Problem:** a class contains an if/else (or switch) choosing between several ways of doing the same job (shipping cost, discount, sorting); adding a way means editing that class. **Solution:** each way becomes a small object behind one interface, and the class receives the one to use. **Trade-off:** more types, and callers must choose. In Java a one-method strategy is just a **functional interface**, so a lambda is often all you need.

## Full Line-by-Line Breakdown

**Before.** `BadShop.shipping(method, kg)` is an if/else on a string; a new method means editing it.

**After.** `ShippingStrategy` (`cost(double kg)`), implemented by `Standard` (4.00 + 0.50 per kg) and `Express` (10.00 + 1.20 per kg). The context `Order` holds a strategy and can **swap it at runtime**:

```
standard: 5.50
express:  13.60   (swapped at runtime)
```

**As lambdas.** `PICKUP = kg -> 0`, `FLAT_RATE = kg -> 7.50`, and a one-off inline `kg -> kg > 5 ? 0 : 3.99`:

```
pickup:   0.00
inline:   3.99   (free over 5 kg, otherwise 3.99)
```

**`Comparator` is a Strategy.** `list.sort(...)` fixes the algorithm; the comparison is the strategy: by price `[pen, lamp, desk]`, by stock descending `[pen, lamp, desk]`.

**Choosing by name.** A `Map<String, ShippingStrategy>` replaces the if/else entirely (2 kg: standard 5.00, express 12.40, pickup 0.00, flat 7.50).

## Key Rules

1. One interface, one implementation per algorithm.
2. The context depends only on the interface.
3. If the interface has one method, use lambdas.
4. Choose strategies by passing them in, or from a map.

## Gotchas Recap

- Two options that will never grow: a plain `if` is shorter.
- Strategies that need most of the context's state end up tangled with it.
- Mutable shared strategies can be a thread-safety problem.

## Why This Structure Exists

The if/else comes first so the refactor is visible. Exit test: an interface with a single implementation "in case we need another later" is speculation, not design.
