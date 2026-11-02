> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Decorator

## Concept

**Problem:** you want optional extras in any combination (milk, sugar, logging, caching). With inheritance you would need a subclass per combination: `CoffeeWithMilkAndSugar`, and so on (an explosion). **Solution:** each extra is a small **wrapper** that implements the same interface, holds the thing it wraps, and adds its bit before or after delegating. Wrappers stack in any order. **Trade-off:** many tiny classes, debugging goes through layers, the **order** of wrappers can matter, and callers cannot tell which wrappers are present.

## Full Line-by-Line Breakdown

**Example 1: coffee.** `Coffee` has `cost()` and `description()`. `PlainCoffee` is the base. `CoffeeDecorator` **is a** `Coffee` and **has a** `Coffee`; `Milk`, `Sugar`, `Syrup` each add to the inner result. Wrappers stack, even repeated ones:

```
coffee                                   $2.00
coffee + milk                            $2.50
coffee + milk + sugar                    $2.70
coffee + milk + sugar + milk + syrup     $3.95
```

**Example 2: a realistic one.** `PriceService` with a `SlowPriceService`, a `LoggingPriceService` and a `CachingPriceService`. With the cache **outside** the logger, repeated items never reach the log:

```
4 calls made, real lookups: 2, log: [priceOf(apple) = 7.5, priceOf(banana) = 9.0]
swapped order, real lookups: 2, log entries: 4
```

Swapping the order keeps the same real lookups but now logs all 4 calls: **order changes behaviour**.

**JDK decorators.** `BufferedReader` wraps any `Reader` (adds buffering and `readLine()`); `Collections.unmodifiableList` wraps a list so writes throw `UnsupportedOperationException`.

## Key Rules

1. A decorator implements the same interface as what it wraps.
2. It delegates, then adds behaviour.
3. Document the intended order of wrappers.
4. Prefer it over a subclass-per-combination.

## Gotchas Recap

- Wrapper order silently changes results (cache vs log above).
- Identity checks (`==`, `instanceof`) see the wrapper, not the inner object.
- Too many layers make stack traces hard to read.

## Why This Structure Exists

The textbook coffee shows the shape; the price service shows why you would really use it. Exit test: when only one extra will ever exist, a subclass or an `if` is clearer; and "does this coffee have milk?" is data, not something to discover by unwrapping.
