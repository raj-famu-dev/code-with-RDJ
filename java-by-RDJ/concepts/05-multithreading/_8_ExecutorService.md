> 📘 Reference material drafted with Claude. Not yet learned: retype `_8_ExecutorService.java`, break it on purpose, then rewrite this walkthrough in your own words.

# ExecutorService

## Concept

Creating a thread per task is expensive and gives you no results, errors or cancellation. An **ExecutorService** is a pool of reusable worker threads plus a task queue: you submit tasks, it decides who runs them.

## Full Line-by-Line Breakdown

**Section 2: a fixed pool of 3.** Six tasks are submitted; the threads are reused:

```
  task 1 ran on pool-1-thread-1
  task 2 ran on pool-1-thread-2
  task 3 ran on pool-1-thread-3
  task 4 ran on pool-1-thread-3
  task 5 ran on pool-1-thread-1
  task 6 ran on pool-1-thread-2
distinct worker threads used: 3 (at most 3)
```

Which thread gets which task varies; the "at most 3" does not.

**Section 3: `execute` vs `submit`.** `submit` returns a `Future` and **hides** an exception until you call `get()`:

```
submit() hid the exception until get(): java.lang.IllegalStateException: task failed
```

If you never call `get()`, the error vanishes silently.

**Section 4: `invokeAll`** runs a batch of `Callable`s, waits for all, and returns futures in submit order: sum of squares 1..5 = 55.

**Section 5: shutting down.** Pool threads are non-daemon, so a forgotten pool keeps the JVM alive. Pattern in `finally`: `shutdown()` (finish queued tasks, accept no more), `awaitTermination(5, SECONDS)`, then `shutdownNow()` if still running.

```
pool.isShutdown() = true, isTerminated() = true
```

**Section 6: after shutdown**, `submit` throws `RejectedExecutionException`.

**Section 7: scheduled pool.** `scheduleAtFixedRate(task, 0, 40, MILLISECONDS)` for about 150 ms gave 4 ticks. The exact count depends on timing.

**Section 8: choosing a pool** (fixed for CPU-bound, cached is unbounded and risky, single for ordering, virtual-thread-per-task for blocking I/O, see `_13`).

## Key Rules

1. Always shut a pool down, in `finally`.
2. Check `submit()` results with `get()`, or errors are lost.
3. Size CPU-bound pools near `availableProcessors()`.
4. `shutdown()` is polite; `shutdownNow()` interrupts.

## Gotchas Recap

- Forgetting `shutdown()` hangs the program at exit.
- `newCachedThreadPool()` can create unbounded threads.
- Tasks that block on other tasks in the same small pool can starve it.

## Why This Structure Exists

It follows the lifecycle of a pool: create, submit, collect, shut down, then the edge cases (rejection, scheduling).
