> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Type Erasure

## Concept

Generics exist only for the **compiler**. After checking your types, the compiler removes them: `List<String>` becomes plain `List` in the `.class` file, with casts inserted where you read. This kept old non-generic code compatible, and it explains most generics restrictions.

## Full Line-by-Line Breakdown

**Section 2: what you cannot do** (all in comments, each a compile error): `new T()`, `new T[10]`, `o instanceof T`, `static T shared`, a generic exception class.

**Runtime proof.**

```
List<String>.getClass()  = java.util.ArrayList
List<Integer>.getClass() = java.util.ArrayList
Same runtime class? true
instanceof List<?> is allowed: true
```

At runtime there is no difference between the two lists. `instanceof List<String>` is a compile error; `instanceof List<?>` is allowed.

**Heap pollution (raw types).** Assigning a `List<String>` to a raw `List` lets you add an `Integer`:

```
list claims to be List<String> yet holds: Integer
ClassCastException far away from the real mistake (the raw add)
```

The failure appears later, at `String s = names.get(0)`, where the compiler-inserted cast fails. This is the main danger of raw types. The compile output shows an `[unchecked]` warning for `raw.add(42)`: that one warning is **deliberate** and is the point of the demo.

**Section 3: generic array workaround.** `SimpleList<T>` creates `(T[]) new Object[4]` and casts it. `@SuppressWarnings("unchecked")` is justified in a comment: the array is private and never leaves the class as a `T[]`. Adding 6 items forces a resize: `SimpleList size = 6, get(5) = f`.

**Section 4: `new T()` workaround.** Pass a `Supplier<T>` (`StringBuilder::new`).

**Section 5: colliding overloads.** `process(List<String>)` and `process(List<Integer>)` have the same erasure, so they cannot coexist.

**Arrays vs generics.** `new List<String>[3]` fails; `new List<?>[3]` is allowed. Arrays know their type at runtime ("reified"), generics do not, so they mix poorly.

## Key Rules

1. Generics are checked at compile time and erased before runtime.
2. No `new T()`, `new T[]`, `instanceof T`, or static fields of type `T`.
3. Never use raw types in new code.
4. Pass a `Supplier<T>` or `Class<T>` when you need to create instances.

## Gotchas Recap

- `ClassCastException` can show up far from the actual mistake.
- `@SuppressWarnings("unchecked")` hides a warning; only use it with a written reason.
- Overloads that differ only in type arguments will not compile.

## Why This Structure Exists

It starts with runtime proof that the types are gone, then the restrictions that follow from it, each with its workaround.
