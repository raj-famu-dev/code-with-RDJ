> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Streams Capstone: Employee Analytics

## Concept

Answer eight business questions about seven employees, **each with one pipeline**, then compare with a plain loop. Uses `groupingBy`, downstream collectors, `partitioningBy`, `flatMap`, `sorted`/`limit`, `Optional`.

## Full Line-by-Line Breakdown

**Data.** An `Employee` record: `name`, `department`, `salary`, `skills` (a list).

**1. Headcount and payroll per department.** `groupingBy` with `counting()` and `summingInt`:

```
1. headcount: {Engineering=3, Operations=2, Security=2}
   payroll:   {Engineering=400000, Operations=175000, Security=275000}
```

**2. Average per department** with `averagingInt`, formatted by `printf("%,10.2f")`: Engineering `133,333.33`, Operations `87,500.00`, Security `137,500.00`.

**3. Highest paid per department** with `maxBy(comparingInt(salary))`: Grace, Margaret, Radia.

**4. Top 3 overall:** `sorted(comparingInt(salary).reversed()).limit(3)`: `[Grace (150000), Radia (140000), Whit (135000)]`.

**5. Above the company average.** Compute the average first (`121,428.57`), then `filter`: `[Ada, Grace, Radia, Whit]`.

**6. Salary bands** with `partitioningBy(salary >= 130000)`.

**7. Skills.** `flatMap(e -> e.skills().stream())` flattens each person's list into one stream, then `groupingBy` + `counting`:

```
7. skills: {c=1, compilers=1, crypto=1, git=2, java=3, math=1, networks=2, planning=2}
   most common skill: java (ties broken alphabetically)
```

**8. Report lines** per department using `joining`.

**Honest comparison.** Question 3 is also solved with a loop (`bestLoop`), and the program checks both agree: `true`. The loop is about 7 lines and easy to follow for **one** question; the stream version scales better when you need **many** group-bys but its nested collectors need practice to read. Neither is always better. (That is your exit-test answer to write in your own words after rewriting one of your own loops.)

## Key Rules

1. `groupingBy` + downstream collector is the core of analytics code.
2. Calculate a shared value (the company average) **before** the pipeline that uses it.
3. Break ties explicitly when sorting or picking a maximum.
4. Check a stream result against a simple loop when you are unsure.

## Gotchas Recap

- `maxBy` returns an `Optional` inside each group: call `.get()` only when you know the group is non-empty (groups from `groupingBy` always are).
- Money as `int`/`double` is a simplification: real money uses `BigDecimal`.
- Output order of a plain `HashMap` is not stable: use `TreeMap` as here.

## Why This Structure Exists

Eight questions, each smaller than the last in surprise, so you can see how the same few tools combine into any report.
