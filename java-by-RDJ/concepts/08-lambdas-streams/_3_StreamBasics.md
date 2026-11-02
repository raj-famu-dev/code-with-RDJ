> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Stream Basics

## Concept

A **stream** is a pipeline that describes what to do with a sequence of values: `SOURCE -> intermediate operations -> TERMINAL operation`. It is **not a collection** (stores nothing), does **not change its source**, and can be used **once**.

## Full Line-by-Line Breakdown

**Section 1: one pipeline.**

```java
names.stream().filter(n -> n.length() > 3).map(String::toUpperCase).sorted().toList();
```

```
pipeline result: [ALAN, GRACE, LINUS, MARGARET]
source is unchanged: [Linus, Ada, Grace, Alan, Margaret, Ada]
```

**Section 2: sources.** `list.stream()`, `Stream.of(..)`, `Arrays.stream(array)`, `IntStream.range(0, 5)` (end excluded) and `rangeClosed(1, 5)` (included), `Stream.iterate(1, n -> n * 2).limit(6)` (infinite, then limited), `Stream.empty()`, `map.entrySet().stream()`, `"abc".chars()`.

**Section 3: intermediate vs terminal.**
- Intermediate (return a Stream, lazy): `filter`, `map`, `flatMap`, `sorted`, `distinct`, `limit`, `skip`, `peek`.
- Terminal (start the pipeline): `collect`, `toList`, `forEach`, `count`, `sum`, `min`, `max`, `reduce`, `anyMatch`, `allMatch`, `noneMatch`, `findFirst`.

**Section 4: single use.**

```
first use works: 6
IllegalStateException: stream has already been operated upon or closed
```

Need it again? Create a new stream from the source.

**Section 5: primitive streams** (`IntStream` and friends) avoid boxing and add `sum()`, `average()`, `summaryStatistics()`:

```
sum of squares 1..5 = 55
average of 1..5 = 3.0
statistics: IntSummaryStatistics{count=6, sum=108, min=4, average=18.000000, max=42}
```

**Section 6: an honest note.** A loop can be clearer when you need several mutable variables, complicated early exits, or checked exceptions in the body.

## Key Rules

1. A pipeline needs a terminal operation to do anything.
2. Streams do not modify the source.
3. One stream, one terminal operation.
4. Use `IntStream` etc. for numbers.

## Gotchas Recap

- Reusing a stream variable throws `IllegalStateException`.
- `range` excludes the end; `rangeClosed` includes it.
- Infinite sources need `limit`, `findFirst` or `anyMatch`.

## Why This Structure Exists

Sources, then operation types, then the one-use rule: it follows the lifetime of a pipeline from creation to the end.
