> 📘 Reference material drafted with Claude. Not yet learned: retype `_6_LazyEvaluation.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Lazy Evaluation

## Concept

Intermediate operations only **describe** the pipeline; nothing runs until a terminal operation. Elements then flow through **one at a time**, and **short-circuiting** operations stop as soon as the answer is known. `peek` (a debugging tool) lets us watch.

## Full Line-by-Line Breakdown

**Section 1: no terminal operation, no work.** The pipeline is built with `peek` and `filter`; nothing prints. Calling `count()` then runs it: all five `peek saw ...` lines appear and `count = 4`.

**Section 2: vertical processing.** Elements go through the **whole** pipeline one at a time, not "all filters, then all maps":

```
  filter Ada
  filter Linus
  map    Linus
  filter Grace
  map    Grace
  ...
```

`Ada` is dropped by the filter, so it never reaches `map`.

**Section 3: short-circuiting.** `findFirst`, `anyMatch`, `allMatch`, `noneMatch` and `limit` stop early:

```
  looking at Ada
  looking at Linus
first long name: Linus   (Alan and Margaret were never examined)
```

and `anyMatch(startsWith("G"))` examined only Ada, Linus, Grace.

**Section 4: infinite streams.** Fine because of laziness: the first 5 powers of two `[1, 2, 4, 8, 16]`; the first 3 multiples of 7 above 100 `[105, 112, 119]`. Without `limit`/`findFirst`/`anyMatch`, an infinite stream never ends (the dangerous line is commented out).

**Section 5: `sorted()` is a barrier.** It must see every element first, so all five `before sorted:` lines print before `limit(2)` can act: `first two alphabetically: [Ada, Alan]`.

**Section 6: side effects are a trap.**

```
count() = 5, peek ran 0 times
```

Since Java 9 `count()` may compute the size directly from the source and **skip the pipeline**, so `peek` never ran. This is why you must not do real work in `peek`/`map`/`filter`.

## Key Rules

1. No terminal operation, no execution.
2. Elements flow one at a time through the whole chain.
3. Short-circuit operations can leave most of the data untouched.
4. `sorted` (and `distinct`) need all data before continuing.
5. `peek` is for debugging only.

## Gotchas Recap

- Side effects inside a pipeline may run fewer times than expected, or not at all.
- An infinite stream plus a non-short-circuiting terminal operation hangs.
- The exact `peek` count for `count()` depends on the JDK version.

## Why This Structure Exists

Every claim about laziness is made visible by printing, so you can see the order rather than take it on trust.
