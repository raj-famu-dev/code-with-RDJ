> 📘 Reference material drafted with Claude. Not yet learned: retype `_2_GenericMethods.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Generic Methods

## Concept

A method can have its own type parameter, declared **before the return type**: `static <T> T firstOf(List<T> items)`. It works for any type, even inside a class that is not generic.

## Full Line-by-Line Breakdown

**Section 1: `printAll` and `firstOf`.** `<T>` is inferred from the argument: pass a `List<String>` and `T` is `String`, so `firstOf` returns a `String` with no cast.

**Section 2: `swap(T[] array, int i, int j)`.** One method for `String[]` and `Integer[]`:

```
swapped words: [three, two, one]
swapped digits: [2, 1, 3]
```

An `int[]` would **not** compile: `T` cannot be a primitive.

**Section 3: two type parameters.** `<A, B> List<B> mapAll(List<A>, Function<A, B>)` converts a list of one type to a list of another:

```
lengths of names: [3, 5, 5]
numbers as labels: [#3, #1, #2]
```

**Section 4: varargs.** `@SafeVarargs static <T> List<T> listOf(T... values)` builds a list from any number of values. `@SafeVarargs` tells the compiler that the method does not misuse the generic array. (The method adds each value in a loop; an earlier version using `Arrays.asList` produced a `[varargs]` warning.)

**Section 5: static factory.** `Holder<T>.of(U value)` uses a **different letter** `U`, because a static method cannot use the class's `T` (it belongs to instances).

**Section 6: inference.** Usually you never write the type. You can: `_2_GenericMethods.<String>listOf("x", "y")`, which is rarely needed.

## Key Rules

1. `<T>` goes before the return type.
2. A static method needs its own type parameter.
3. Inference works from the arguments (and sometimes the target type).
4. Arrays and collections of primitives do not work: use `Integer[]`.

## Gotchas Recap

- Writing the return type first (`T <T> foo()`) is a syntax error.
- Reusing the class's `T` as a static method's parameter produces a confusing error.
- Heavy inference can give surprising types: hover in your IDE when in doubt.

## Why This Structure Exists

The examples escalate from one parameter to two to static factories, which is the order in which you will meet them in real code (`Collections`, `Stream.map`, `Optional.of`).
