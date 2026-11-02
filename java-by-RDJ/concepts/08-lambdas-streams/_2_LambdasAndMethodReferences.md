> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Lambdas and Method References

## Concept

A **lambda** is an inline implementation of a functional interface. A **method reference** (`Class::method`) is an even shorter form when a lambda only calls one existing method.

## Full Line-by-Line Breakdown

**Section 1: one task, four styles.** Sorting `Linus(55), Ada(36), Grace(85)` by age:
1. Anonymous class: lots of ceremony.
2. Lambda: `(p1, p2) -> Integer.compare(p1.getAge(), p2.getAge())`.
3. Method reference: `Person::compareByAge` (an existing static method).
4. `Comparator.comparingInt(Person::getAge)`: the idiomatic form.

All four give `[Ada(36), Linus(55), Grace(85)]`.

**Section 2: lambda syntax.**
```
(parameters) -> expression
(parameters) -> { statements; return value; }
```
Four spellings of "square" (full types, inferred, no parentheses, block body with `return`) agree. No parameters needs `()`.

**Section 3: the four kinds of method reference.**
1. static: `Integer::parseInt`
2. on a given object: `prefix::concat`, `System.out::println`
3. on the parameter: `Person::getName` means `p -> p.getName()`
4. constructor: `ArrayList::new`

**Section 4: a lambda is not an anonymous class.** Inside a lambda, `this` is the **surrounding** object; inside an anonymous class, `this` is the anonymous object (its class name is empty):

```
lambda 'this' is the outer object, class = _2_LambdasAndMethodReferences
anonymous 'this' is the anonymous object, class name empty: true
```

**Section 5: capturing variables.** A lambda may use local variables only if they are **effectively final** (never reassigned): `base = 100` works (`105`). `total += ...` inside a lambda is a compile error. The one-element array trick works (`176`) but is a code smell. Fields can be changed (`3`), though shared mutable state is risky with streams.

## Key Rules

1. A lambda needs a functional interface as its target type.
2. Use a method reference when the lambda only forwards to one method.
3. Captured locals must be effectively final.
4. `this` in a lambda is the enclosing object.

## Gotchas Recap

- Ambiguous method references (overloads) may not compile; fall back to a lambda.
- Mutating captured state from a lambda is a bug magnet.
- `Person::getAge` (unbound) and `holder::method` (bound) look alike but differ.

## Why This Structure Exists

The same task is written four ways so the lambda and method reference are seen as shortenings of the code you already know, not new magic.
