> 📘 Reference material drafted with Claude. Not yet learned: retype `_7_OptionalDoneRight.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Optional Done Right

## Concept

`Optional<T>` holds either one value or nothing. Its purpose is to make "this result may be absent" part of a method's **return type**, so callers cannot forget. It is a return-type tool, not a general null replacement.

## Full Line-by-Line Breakdown

**Section 1.** `UserRepository.findByName` returns `Optional<User>`. Printed: `Optional[User[name=ada, email=ada@example.com]]` and `Optional.empty`. `found.isPresent(): true, missing.isEmpty(): true`.

**Section 2: creating.** `Optional.of(value)` (value must not be null: `of(null)` throws `NullPointerException`), `Optional.ofNullable(x)` (null becomes empty), `Optional.empty()`.

**Section 3: getting the value, the good ways.**
- `orElse("default-name")`
- `orElseGet(() -> ...)`: the supplier runs **only when needed** (`orElse(x)` always builds `x`, so use `orElseGet` for anything costly)
- `orElseThrow(() -> new NoSuchElementException("user not found"))`

**Section 4: the bad way.** `get()` on an empty Optional throws `NoSuchElementException: No value present`. `isPresent()` followed by `get()` is a null check in disguise; prefer `map`/`orElse`/`ifPresent`.

**Section 5: transforming without unwrapping.** `map` applies a function if present; a **null result from `map` becomes empty** (that is why Linus, who has no email, gives `Optional.empty` instead of an NPE). `filter` keeps the value only if it passes. `flatMap` is for functions that themselves return an Optional.

```
whole chain with a default: no-email@unknown
same result the old way:    no-email@unknown
```

**Section 6: doing something only if present.** `ifPresent`, `ifPresentOrElse`, and `or(() -> Optional.of(...))` for a fallback Optional.

**Section 7: where NOT to use it.**
- Not as a **field** (not `Serializable`, extra object).
- Not as a method **parameter**.
- Not inside collections: return an empty list, never `null` or `Optional<List>`.
- Not as a replacement for a plain local null check.
- Never assign `null` to an Optional variable.

**Section 8: primitive versions.** `OptionalInt`/`OptionalDouble` come back from `max()` and `average()`: an empty `IntStream` average prints `OptionalDouble.empty`.

## Key Rules

1. Return `Optional` when "no result" is a normal outcome.
2. Use `map`/`orElse`/`orElseGet`/`orElseThrow`, not `isPresent()` + `get()`.
3. `orElseGet` for costly defaults.
4. Never use Optional for fields or parameters.

## Gotchas Recap

- `Optional.of(null)` throws.
- `orElse(expensiveCall())` runs the call every time.
- Calling `get()` unchecked reintroduces the exact bug Optional exists to prevent.

## Why This Structure Exists

The "where not to use it" section is as important as the how: most Optional misuse is using it where it does not belong.
