> 📘 Reference material drafted with Claude. Not yet learned: retype `_2_RunnableAndCallable.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Runnable and Callable

## Concept

`Runnable` describes work that returns nothing. `Callable<V>` describes work that **returns a value** and may throw a checked exception. A `Future` (here a `FutureTask`) is a handle to a result that may not be ready yet.

## Full Line-by-Line Breakdown

**Section 1: Runnable.** `void run()` cannot return anything, so the example smuggles `42` out through a one-element array. This is awkward, and without `join()` the array could still hold 0 when read.

**Section 2: Callable + FutureTask.**

```
isDone right away? false
get() waits, then returns: 42
isDone now? true
```

`new FutureTask<>(job)` wraps the `Callable` so that a plain `Thread` can run it. `get()` blocks until the result is ready.

**Section 3: checked exceptions.**

```
get() threw ExecutionException, cause = java.io.IOException: disk full
```

A `Callable` may throw `IOException`. The error is captured and re-delivered, wrapped in `ExecutionException`, when you call `get()`. The original is `getCause()`. The commented-out `Runnable` line would not compile: `run()` allows no checked exceptions.

**Section 4: timeouts.** `get(100, MILLISECONDS)` gives up with `TimeoutException`. `cancel(true)` then interrupts the worker, and `isCancelled()` becomes `true`. The slow thread is a daemon so it can never keep the JVM alive.

**Section 5: summary** of the four types.

## Key Rules

1. `Runnable.run()`: void, no checked exceptions. `Callable.call()`: returns `V`, may throw `Exception`.
2. `Future.get()` blocks; prefer `get(timeout, unit)`.
3. Failures arrive as `ExecutionException`; look at `getCause()`.
4. `cancel(true)` is a request (an interrupt), not a guaranteed kill.

## Gotchas Recap

- Calling `get()` with no timeout on a task that never finishes freezes your thread.
- `ExecutionException` is the wrapper, not the real error.
- A `Future` hides exceptions until you call `get()`.

## Why This Structure Exists

You see the pain of `Runnable` first (the array trick) so that `Callable` feels like the fix it is. Executors (`_8`) then do the `FutureTask` wrapping for you.
