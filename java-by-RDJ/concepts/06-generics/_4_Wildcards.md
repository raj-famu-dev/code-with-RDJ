> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Wildcards and PECS

## Concept

Even though `Dog` is an `Animal`, a `List<Dog>` is **not** a `List<Animal>`. Wildcards (`?`) let a method accept a family of generic types safely.

## Full Line-by-Line Breakdown

**Section 1: why `List<Dog>` is not a `List<Animal>`.** If it were, you could add a `Cat` through the `List<Animal>` view and pollute the list of dogs. The same reason makes `List<Object>` not a supertype of `List<String>`. Arrays **do** allow this, and it fails at runtime instead:

```
Arrays: ArrayStoreException at runtime. Generics stop this at compile time.
```

**Section 2: `?` (unknown).** `count(List<?> list)` only uses `size()`:

```
count of dogs: 2
count of cats: 1
```

**Section 3: `? extends T` is a producer.** `printNames(List<? extends Animal>)` accepts `List<Dog>` and `List<Cat>`. You can **read** (everything is at least an `Animal`) but not **add**: the list might really be a `List<Cat>`. Only `null` can be added.

**Section 4: `? super T` is a consumer.** `addDogs(List<? super Dog>)` accepts `List<Animal>` and `List<Object>`. You can **add** a `Dog` (it fits whichever it is) but reading gives only `Object`:

```
animals after addDogs: 2, objects after addDogs: 2
read from ? super gives only Object: Dog
```

(The printed `Dog` is the runtime class of the object; the compile-time type is `Object`.)

**Section 5: PECS = Producer Extends, Consumer Super.** `copy(List<? extends T> source, List<? super T> destination)`: the source produces, the destination consumes. Copying dogs into a `List<Animal>` gives `2 items`.

**Section 6: summary table.**

| | read | write |
|---|---|---|
| `List<?>` | `Object` | nothing (only null) |
| `List<? extends T>` | `T` | nothing (only null) |
| `List<? super T>` | `Object` | `T` |
| `List<T>` | `T` | `T` |

## Key Rules

1. Generics are invariant: `List<Dog>` is not a `List<Animal>`.
2. Read from it: `? extends T`. Write into it: `? super T`. Both: exact type.
3. Use `?` when you do not care about the element type.

## Gotchas Recap

- You cannot add to a `List<? extends T>` (not even a `T`).
- You cannot read a useful type from `List<? super T>`.
- Wildcards are for method parameters; do not use them as return types.

## Why This Structure Exists

The surprising rule (not a subtype) comes first, then each wildcard solves one half of it. The exit-test answer ("explain PECS") is Section 5.
