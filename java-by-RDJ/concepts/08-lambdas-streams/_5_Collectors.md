> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Collectors

## Concept

`collect(...)` is the terminal operation that gathers a stream into a result; a **Collector** says how. `Collectors.*` has ready-made ones. Data: six `Person` records (a record is a small class with fields and accessors such as `name()`; see `09`).

Map results are copied into `TreeMap`s so the printed order is stable (a `HashMap`'s iteration order should never be relied on).

## Full Line-by-Line Breakdown

**Section 1: collections.** `toList`, `toCollection(TreeSet::new)` (sorted, distinct: `[Helsinki, London, New York]`), and the newer `Stream.toList()` (unmodifiable).

**Section 2: `joining(", ", "{", "}")`** gives `{Ada, Alan, Grace, Linus, Margaret, Tim}`.

**Section 3: `toMap`.** Key function and value function. If two elements make the same key it throws:

```
duplicate key -> IllegalStateException: Duplicate key London (attempted merging values Ada and Alan)
```

A third argument, the **merge function**, resolves clashes: `{Helsinki=Linus, London=Ada+Alan+Tim, New York=Grace+Margaret}`.

**Section 4: `groupingBy`** is SQL's GROUP BY. `groupingBy(classifier, mapFactory, downstream)`; the **downstream collector** decides what happens inside each group:

```
names by city:       {Helsinki=[Linus], London=[Ada, Alan, Tim], New York=[Grace, Margaret]}
count by city:       {Helsinki=1, London=3, New York=2}
average age by city: {Helsinki=55.0, London=35.333333333333336, New York=57.0}
sum of ages by city: {Helsinki=55, London=106, New York=114}
oldest in London: Alan
```

(`mapping`, `counting`, `averagingInt`, `summingInt`, `maxBy` are the downstream collectors used.)

**Section 5: `partitioningBy`.** Exactly two groups, `true` and `false`, always both present: age >= 40 `[Alan, Grace, Linus]`, below `[Ada, Margaret, Tim]`.

**Section 6: summaries.** `summarizingInt` gives count, sum, min, average, max in one object (`count=6, sum=275, min=29, average=45.833333, max=85`).

**Section 7: which one?** List/set: `toList`/`toSet`; one string: `joining`; lookup table: `toMap`; group plus something: `groupingBy`; yes/no split: `partitioningBy`.

## Key Rules

1. `toMap` throws on duplicate keys unless you give a merge function.
2. Combine `groupingBy` with a downstream collector for real analytics.
3. `partitioningBy` always has both keys.
4. Do not depend on `HashMap` ordering in output.

## Gotchas Recap

- `averagingInt` returns a `double` (`35.333333333333336`): format when printing.
- `toMap` also throws `NullPointerException` for null values.
- `Collectors.toList()` makes a modifiable list; `Stream.toList()` does not.

## Why This Structure Exists

It goes from simple containers to grouping, because `groupingBy` with a downstream collector is the one you will use most.
