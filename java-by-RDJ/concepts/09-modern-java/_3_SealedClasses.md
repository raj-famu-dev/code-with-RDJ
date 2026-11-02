> 📘 Reference material drafted with Claude. Not yet learned: retype `_3_SealedClasses.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Sealed Classes and Interfaces

## Concept

A normal interface can be implemented by anyone. A **sealed** type lists exactly which types may extend it (`permits`), so the compiler knows **every** possible case.

## Full Line-by-Line Breakdown

**Section 2: `sealed interface Shape permits Circle, Rectangle, Triangle`.** Each permitted subtype must be `final`, `sealed` or `non-sealed`. Records are implicitly final, so `Circle` and `Rectangle` qualify; `Triangle` is an explicit `final class`.

**Section 3: the reward, an exhaustive `switch`.**

```java
return switch (shape) {
    case Circle c -> ...
    case Rectangle r -> ...
    case Triangle t -> ...
};          // no default needed
```

Add a fourth shape later and every switch that forgot it stops **compiling**. Bugs move from runtime to compile time.

```
Circle     area = 3.14
Rectangle  area = 6.00
Triangle   area = 10.00
```

**Section 4: the three choices.**
- `final`: the end of the line (`Car`, `PickUp`, `Lorry`).
- `sealed`: opens another closed family below it (`Truck permits PickUp, Lorry`).
- `non-sealed`: deliberately re-opens a branch (`Custom`), so `Hovercraft` is allowed and the switch must cover `Custom`.

**Section 5: a `Result<T>`** that is either `Success<T>` or `Failure<T>`: the type states which outcomes exist (`ok: 42`, `failed: 'forty-two' is not a number`).

**What the compiler refuses (comments):** a type not in `permits`; a `permits` entry that does not extend the type; a non-exhaustive switch.

**Section 6 rules.** Permitted subtypes must be in the same module (or same package without modules). In a single file they can be nested and `permits` may be omitted. Sealed + records + pattern switch = "algebraic data types".

## Key Rules

1. Use `sealed` when the set of cases is truly fixed.
2. Every permitted subtype declares `final`, `sealed` or `non-sealed`.
3. Switch over a sealed type needs no `default`: let the compiler check completeness.
4. For open-ended extension, use a normal interface.

## Gotchas Recap

- `default` in a switch over a sealed type defeats the compile-time check.
- A `non-sealed` branch re-opens the hierarchy: the switch must cover it.
- Forgetting to list a new subtype in `permits` is a compile error (a good one).

## Why This Structure Exists

Shapes show the basic idea, vehicles show all three subtype choices, and `Result` shows the pattern you will actually use in applications.
