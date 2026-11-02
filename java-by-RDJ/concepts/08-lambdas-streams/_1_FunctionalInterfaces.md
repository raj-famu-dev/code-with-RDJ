> 📘 Reference material drafted with Claude. Not yet learned: retype `_1_FunctionalInterfaces.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Functional Interfaces

## Concept

A **functional interface** has exactly **one abstract method**. Because there is only one thing to implement, Java lets you write it as a short **lambda**. `@FunctionalInterface` makes the compiler check the rule. `java.util.function` already has the shapes you need.

## Full Line-by-Line Breakdown

**Section 1-2: your own.** `Greeter` has one abstract method `greet` and a `default` method `greetLoudly`. Default and static methods do not count against the one-abstract-method rule. `Greeter friendly = name -> "Hello, " + name;`

```
Hello, Ada
HELLO, ADA!
```

A second abstract method would be a compile error (shown commented out).

**Section 3: the built-in shapes.**

| Interface | Shape | Method |
|---|---|---|
| `Function<T,R>` | T -> R | `apply` |
| `Predicate<T>` | T -> boolean | `test` |
| `Consumer<T>` | T -> nothing | `accept` |
| `Supplier<T>` | nothing -> T | `get` |
| `BiFunction<T,U,R>` | (T,U) -> R | `apply` |
| `UnaryOperator<T>` | T -> T | `apply` |
| `BinaryOperator<T>` | (T,T) -> T | `apply` |

Examples run: `length("streams") = 7`, `isEven(10) = true`, `add(3, 4) = 7`, `max(8, 5) = 8`.

**Section 4: primitive versions** (`IntPredicate`, `ToIntFunction`) avoid boxing every `int` into an `Integer`.

**Section 5: combining.**
- `and`, `or`, `negate` on predicates: `"tree" -> true`, `"" -> false` for `notEmpty.and(shortWord)`.
- `andThen` = first this, then that; `compose` = first that, then this:

```
plusOne.andThen(doubled)(5) = 12   (5+1)*2
plusOne.compose(doubled)(5) = 11   (5*2)+1
```

- `Function.identity()` returns its input.

**Section 6: functions are values.** Store them in a `List<Function<..>>` and apply in order (`4 -> 5 -> 50 -> 47`), or pass them to a method (`applyTwice(n -> n * n, 3)` gives `81`).

## Key Rules

1. One abstract method = lambda-able.
2. Learn the five core shapes: `Function`, `Predicate`, `Consumer`, `Supplier`, `BiFunction`.
3. `andThen` and `compose` run in opposite orders.
4. Prefer primitive variants when numbers are involved.

## Gotchas Recap

- Mixing up `andThen` and `compose` gives off-by-one style bugs (12 vs 11 above).
- `Consumer` returns nothing, so you cannot chain it into a result.
- A lambda needs a **target type**: `var f = x -> x;` does not compile.

## Why This Structure Exists

Everything later in this folder (streams, collectors, Optional) takes one of these shapes as an argument, so they come first.
