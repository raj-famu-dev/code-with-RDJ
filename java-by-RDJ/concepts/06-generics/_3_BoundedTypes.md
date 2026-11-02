> 📘 Reference material drafted with Claude. Not yet learned: retype `_3_BoundedTypes.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Bounded Types

## Concept

A plain `<T>` tells you nothing about `T` except that it is an `Object`, so you cannot compare or add two `T`s. A **bound** (`<T extends Comparable<T>>`) narrows `T` so that useful methods become available, and the compiler enforces it.

## Full Line-by-Line Breakdown

**Section 1: the problem.** `a > b` fails (only numbers), and `a.compareTo(b)` fails (`Object` has no `compareTo`). Both are in comments.

**Section 2: `T extends Comparable<T>`.** `extends` here means "extends **or implements**". Now `compareTo` exists:

```
max(3, 9)           = 9
max("pear", "apple") = pear
max(2.5, 1.5)      = 2.5
```

`maxOf(List<T>)` and `countGreaterThan(List<T>, T)` use the same bound: `maxOf(scores) = 91`, `countGreaterThan(70) = 3`.

`max(new Object(), new Object())` and `max(1, "a")` do not compile.

**Section 3: bound to a class.** `<T extends Number>` gives `doubleValue()`, so `sum` works for `Integer` and `Double` lists but not `String`:

```
sum of Integers     = 6.0
sum of Doubles      = 4.0
```

**Section 4: bounded class.** `MaxTracker<T extends Comparable<T>>` keeps the biggest value offered: for `kiwi, fig, plum, banana` it holds `plum` (alphabetically last).

**Section 5: multiple bounds.** `<T extends Named & Comparable<T>>`: if one bound is a class it must be listed first; the rest are interfaces. `nameOfBest` uses `compareTo` from one and `name()` from the other: `highest paid = Linus`.

## Key Rules

1. `<T extends X>`: `T` is `X` or any subtype (class or interface).
2. A bound lets you call `X`'s methods on a `T`.
3. Bounds are enforced at compile time.
4. `<T extends Comparable<T>>` is the standard "can be ordered" pattern (library code often uses `Comparable<? super T>`, see `_4` and `_6`).

## Gotchas Recap

- `sum` returns `6.0` for integers because it accumulates a `double`: the bound only guarantees `doubleValue()`.
- Multiple bounds: class first, otherwise a compile error.
- `max(1, 2.5)` does not compile: `T` would have to be both `Integer` and `Double`.

## Why This Structure Exists

It shows the bound as the answer to a concrete compile error, not an abstract rule.
