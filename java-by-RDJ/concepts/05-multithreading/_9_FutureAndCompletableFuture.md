> 📘 Reference material drafted with Claude. Not yet learned: retype `_9_FutureAndCompletableFuture.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Future and CompletableFuture

## Concept

`Future.get()` blocks, so you cannot say "when this finishes, do that". **CompletableFuture** lets you build a pipeline of steps that run as results arrive. We pass our own executor everywhere so we control (and shut down) the threads.

## Full Line-by-Line Breakdown

**Section 2: `supplyAsync` + `thenApply`.** Start work in the background and transform the result (like `map`): `Hello, user-7`.

**Section 3: `thenCompose`.** Use when step 2 is itself async and needs step 1's result. `thenApply` would give a nested `CompletableFuture<CompletableFuture<..>>`; `thenCompose` flattens it (like `flatMap`): `score of user 3 = 30`.

**Section 4: `thenCombine`.** Two independent 50 ms calls started together, then merged:

```
user-5 has score 50  (took about 60 ms; two 50 ms calls ran in parallel)
```

The timing is a measurement from this machine, not a promise.

**Section 5: `allOf`.** Waits for many futures. It returns `CompletableFuture<Void>`, so you read each result afterwards with `join()` (like `get()` without checked exceptions). Total of three scores = 60. The array is created as `new CompletableFuture<?>[0]` to avoid a raw-type warning.

**Section 6: errors flow down the pipeline.** A failing stage makes later `thenApply` stages skip:

```
exceptionally -> -1
handle        -> failed: service down
join() wraps it in CompletionException, cause = java.lang.IllegalStateException: service down
```

`exceptionally` supplies a fallback only on failure; `handle` always runs with `(result, error)`.

**Section 7: timeouts.** `completeOnTimeout("default", 100, MILLISECONDS)` supplies a default if the 1.5 s task is too slow: `slow call with fallback: default`. (`orTimeout` fails the future with `TimeoutException` instead.)

**Section 8: the default pool.** Without an executor, `ForkJoinPool.commonPool()` is used: few daemon threads, wrong for blocking calls. The `finally` calls `shutdownNow()` to drop the leftover 1.5 s sleeper.

## Key Rules

1. `thenApply` = map, `thenCompose` = flatMap, `thenCombine` = merge two.
2. Errors skip the normal stages and reach `exceptionally`/`handle`.
3. Pass your own executor for blocking work.
4. Add a timeout to anything that talks to the outside world.

## Gotchas Recap

- `join()` throws `CompletionException`; `get()` throws `ExecutionException`.
- Without an error handler, a failure is silent until someone calls `get`/`join`.
- `allOf` gives no results by itself.

## Why This Structure Exists

Each section adds one idea to the same pipeline, in the order you would meet them: chain, flatten, combine, fan-in, fail, time out.
