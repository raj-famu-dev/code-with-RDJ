> 📘 Reference material drafted with Claude. Not yet learned: retype `_1_GenericClasses.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Generic Classes

## Concept

A generic class has a **type parameter** (`<T>`): a placeholder filled in by whoever uses the class. `Box<String>` means "a Box where T is String". It gives you reuse (one class for every type) **and** compile-time type safety (no casts).

## Full Line-by-Line Breakdown

**Section 1: the `Object` problem.** `ObjectBox` stores an `Object`. You must cast on the way out, and a wrong guess is found only when the line runs:

```
ObjectBox, after a cast: hello
ClassCastException at RUNTIME: the compiler could not warn us
```

**Section 2: `Box<T>`.** `T` is used for the field, constructor, `get()` and `set()`. `new Box<>("Ada")` uses the **diamond** `<>` so Java infers `String`. No cast needed, and `new Box<>(42)` assigned to `Box<String>` is a compile error (caught before the program runs).

```
Box<String>: Box[Ada], get() = Ada
Box<Integer>: Box[15]
```

**Section 3: `Pair<A, B>`.** Two type parameters. `swap()` returns a new `Pair<B, A>` with the types flipped.

```
Pair: (age, 30), swapped: (30, age)
key = age, value = 30
```

**Section 4: `Bag<T>`.** A class that uses `T` inside a `List<T>`.

**Section 5 rules:** type arguments must be object types (`Box<Integer>`, never `Box<int>`; boxing is automatic), naming convention (`T` type, `E` element, `K` key, `V` value), and no `new T()` (see `_5`).

## Key Rules

1. `class Box<T>` declares a type parameter; `Box<String>` supplies it.
2. Use the diamond `<>` on the right-hand side.
3. No primitives as type arguments: use the wrapper types.
4. Generics move a whole class of bugs from runtime to compile time.

## Gotchas Recap

- `Box<Object>` is not the same as `Box` (raw type); never use the raw form.
- Autoboxing hides a cost: `Integer` objects, and unboxing `null` throws `NullPointerException`.
- `T` is not a real type you can instantiate.

## Why This Structure Exists

Starting with the broken `ObjectBox` makes the benefit concrete: you see the exact failure generics remove.
