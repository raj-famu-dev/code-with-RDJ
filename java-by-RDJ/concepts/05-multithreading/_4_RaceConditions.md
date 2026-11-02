> 📘 Reference material drafted with Claude. Not yet learned: retype `_4_RaceConditions.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Race Conditions

## Concept

A **race condition** is a bug where the result depends on how two threads happen to interleave. The classic form is a lost update on a shared counter.

## Full Line-by-Line Breakdown

**Section 1: `value++` is three steps.** Read, add 1, write back. If threads A and B both read 5, both write 6, and two increments moved the counter by one.

**Section 2: watching it fail.** Two threads, 500,000 increments each (expected 1,000,000). Two separate runs on this machine:

```
run 1: expected 1000000, got 973089  (lost 26911)
run 4: expected 1000000, got 1000000  (lucky: no update lost this time)
```

```
run 3: expected 1000000, got 905243  (lost 94757)
run 4: expected 1000000, got 595121  (lost 404879)
```

The wrong totals differ every run, and some runs are correct by luck. That is why races are hard to find: a passing test proves nothing.

**Section 3: one thread** always gives 1,000,000. The bug needs shared data and two or more threads.

**Section 4: check-then-act.** Balance 100, two threads each withdraw 80. The code checks `balance >= amount`, then subtracts. `Thread.yield()` between check and act makes the gap easier to hit, and a `CyclicBarrier` makes both threads start together. Result on this machine: negative in 98 of 2000 trials, then 87 of 2000 on another run. It varies, and can be 0 on a slow or single-core machine.

## Key Rules

1. A race needs: shared data, at least one writer, no coordination.
2. `x++`, `x += n` and "check, then act" are never atomic by themselves.
3. Race failures are intermittent. Never conclude "it passed, so it is safe".
4. The fixes: `synchronized` (`_5`), locks and atomics (`_10`), or share nothing (`_14`).

## Gotchas Recap

- Do not assert a specific wrong number: it is different on every machine.
- Adding `println` to debug can hide a race by changing the timing.
- Fewer iterations make the bug look absent.

## Why This Structure Exists

You have to see the bug before the fix means anything. This file shows two different families (read-modify-write and check-then-act) so that you recognise the pattern, not just the counter.
