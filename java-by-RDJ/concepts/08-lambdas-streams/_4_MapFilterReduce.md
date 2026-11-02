> 📘 Reference material drafted with Claude. Not yet learned: retype `_4_MapFilterReduce.java`, break it on purpose, then rewrite this walkthrough in your own words.

# map, filter, flatMap, reduce and friends

## Concept

The everyday intermediate operations plus `reduce`. Data used: `numbers = [5, 3, 8, 3, 1, 9, 8, 2]` and `words = [stream, lambda, filter, map, reduce]`.

## Full Line-by-Line Breakdown

**`filter` (Predicate): keep what matches.** `filter even -> [8, 8, 2]`.

**`map` (Function): one in, one out.** Squares: `[25, 9, 64, 9, 1, 81, 64, 4]`; lengths: `[6, 6, 6, 3, 6]`.

**`flatMap`: one in, many out, then flatten.**

```
map gives lists:    [[1, 2], [3], [4, 5, 6]]
flatMap flattens:   [1, 2, 3, 4, 5, 6]
all words:          [to, be, or, not, to, be]
```

**`sorted`, `distinct`, `limit`, `skip`.**

```
sorted:             [1, 2, 3, 3, 5, 8, 8, 9]
sorted descending:  [9, 8, 8, 5, 3, 3, 2, 1]
distinct:           [5, 3, 8, 1, 9, 2]
limit 3:            [5, 3, 8]
skip 5:             [9, 8, 2]
sorted by length then alphabetically: [map, filter, lambda, reduce, stream]
```

**`reduce`: fold everything into one value.** `reduce(0, (acc, n) -> acc + n)` starts from the **identity** (the do-nothing value: 0 for `+`, 1 for `*`) and folds each element in: sum `39`, product of 1..4 `24`. Without an identity the stream might be empty, so the result is an `Optional`:

```
reduce max:         9, on an empty stream: Optional.empty
```

**Numbers the easy way.** `mapToInt(..).sum()` is simpler than `reduce`.

**A complete pipeline.** Squares of 1..10, keep the even ones, sort descending, take 3, join as text: `[100, 64, 36]`.

**Order matters.** Filtering early means later steps do less work (the last section shows two equal pipelines in a comment).

## Key Rules

1. `map` = transform, `filter` = keep, `flatMap` = flatten nested.
2. `reduce` needs an identity that really is neutral.
3. `sorted` with a comparator: `Comparator.comparingInt(..).thenComparing(..)`.
4. Prefer `sum`/`max`/`average` on primitive streams to hand-written `reduce`.

## Gotchas Recap

- A wrong identity (e.g. `1` for a sum) silently gives wrong totals.
- `distinct` uses `equals`/`hashCode`.
- `sorted()` on objects that are not `Comparable` fails at runtime with `ClassCastException`.

## Why This Structure Exists

One operation per section with its own printed result, so you can test each by changing one number.
