# `_5_FuturesPromisesAsync.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A `std::future<T>` is a handle to a result that will be available later, possibly computed on another thread. `std::async` runs a function and hands you the future; `std::promise` is the writing end that you fulfil yourself with `set_value` or `set_exception`; `std::packaged_task` wraps a callable so you control where and when it runs and still get a future. Exceptions thrown in the worker travel through the future and are rethrown by `get()`. Compile with `-pthread`.

## Full Line-by-Line Breakdown

### SECTION 1: std::async AND std::future
`std::async(std::launch::async, f, args...)` starts `f` on a new thread and returns a `future`. Two tasks sum the two halves of 1..1000 and `get()` blocks until each is done; the total is 500500. `std::cref(data)` passes a const reference (arguments are copied unless wrapped, as in the threads file). `valid()` is true before `get()` and false after: a future's value can be taken only once. With `std::launch::deferred` nothing runs until `get()`, and then it runs in the calling thread. TRAP: the default policy lets the implementation choose either, so always state the launch policy.

Output from a real run:

```text
===== SECTION 1: std::async AND std::future =====
future valid before get(): true
sum 1..1000 computed by two async tasks = 500500 (expected 500500)
future valid after get(): false (a future's value can be taken only ONCE)
deferred task result: 99
```

### SECTION 2: EXCEPTIONS TRAVEL THROUGH FUTURES
A task that throws does not crash the other thread: the exception is stored in the shared state and rethrown by `get()` in the caller. `risky(21)` returns 42, `risky(-1)` throws `std::invalid_argument`, and the caller's `catch` receives it with the original message. This is the safest way to report errors from worker threads (an exception escaping a plain `std::thread` function calls `std::terminate`).

Output from a real run:

```text
===== SECTION 2: EXCEPTIONS TRAVEL THROUGH FUTURES =====
risky(21) -> 42
get() rethrew the worker's exception: negative input
```

### SECTION 3: std::promise
A `std::promise<T>` and its `future` are two ends of a channel. The worker calls `set_value`, the main thread calls `get()`. `std::promise` is movable but not copyable, so it is moved into the thread's lambda (the lambda is `mutable` so it can call the non-const `set_value`). A worker can also report failure with `p.set_exception(std::current_exception())`, which the waiting side sees as a rethrown exception. If a promise is destroyed without being fulfilled, `get()` throws `std::future_error` with code `broken_promise`, so waiters are never stuck forever.

Output from a real run:

```text
===== SECTION 3: std::promise =====
main received: value delivered through a promise
promise::set_exception delivered: worker could not finish
abandoned promise -> future_error, code is broken_promise: true
```

### SECTION 4: std::packaged_task
`std::packaged_task<int(int,int)>` wraps a callable together with a future for its result. You decide how to run it: here it is moved into a `std::thread` and called with 6 and 7, and `get()` returns 42. The second block is the typical pattern behind thread pools: a vector of tasks, each with its future, which some worker later runs; here they are simply run on the main thread, giving 100, 200, 300. Tasks are move-only.

Output from a real run:

```text
===== SECTION 4: std::packaged_task =====
packaged_task result: 42
queued tasks results: 100 200 300
```

### SECTION 5: wait_for AND THE BLOCKING-DESTRUCTOR TRAP
`wait_for(duration)` returns `future_status::timeout` if the result is not ready yet and `ready` once it is, so you can poll or give up. TRAP: the destructor of a future returned by `std::async` (launch policy `async`) BLOCKS until the task finishes. `std::async(...)` with the result discarded therefore is not "fire and forget": the temporary future is destroyed immediately and the call waits. The demo shows that the discarded call really blocked at least 60 ms; it prints only the boolean because the exact number of milliseconds is a measurement that varies, and the line says so. (A `(void)` cast is used to silence the `[[nodiscard]]` warning, which exists precisely to catch this mistake.)

Output from a real run:

```text
===== SECTION 5: wait_for AND THE BLOCKING-DESTRUCTOR TRAP =====
wait_for on an unfinished future -> timeout: true
wait_for after set_value -> ready: true
TRAP: calling 'std::async(std::launch::async, f);' and ignoring the returned future makes the
      temporary future's destructor BLOCK until f finishes, so it is not 'fire and forget'.
      Always keep the future in a variable and call get() or wait().
the discarded async call blocked for at least 60 ms: true (MEASUREMENT: exact milliseconds vary and are not printed)
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `CompletableFuture.supplyAsync(() -> ...)` runs on the common ForkJoinPool. | `std::async(std::launch::async, ...)` usually starts a new thread; no shared pool is guaranteed. |
| `future.get()` throws `ExecutionException` wrapping the cause. | `future.get()` rethrows the ORIGINAL exception type. |
| `thenApply`, `thenCompose`, `thenCombine`, `allOf` for chaining and combining. | No continuations in C++20 `std::future`; you block with `get()` or build your own chaining. |
| `CompletableFuture.complete(value)` / `completeExceptionally(ex)` from any thread. | `std::promise::set_value` / `set_exception` (once only). |
| `ExecutorService.submit(callable)` gives a `Future`. | `std::packaged_task` plus your own threads or pool gives a `future`. |
| `Future` ignored: the task simply runs. | An `async` future that is destroyed blocks until the task is done. |
| `future.get(timeout, unit)` | `future.wait_for(duration)` returns a status; then `get()`. |

## Key Rules / Gotchas Recap
- Always pass `std::launch::async` (or `deferred`) explicitly.
- Keep the future in a variable and call `get()` or `wait()`; a discarded `async` future blocks.
- `get()` can be called once; use `std::shared_future` if several threads need the value.
- Exceptions come back through `get()`.
- A promise must be fulfilled (or destroyed, giving `broken_promise`); fulfilling twice throws `future_error`.
- `promise` and `packaged_task` are move-only.
- `std::future` has no `then()`; for pipelines you need another library or your own code.

## Why This Structure Exists
Fan-out/fan-in (split a job, compute parts in parallel, combine) and "run this on a worker and give me the answer" are everyday needs: parallel feature extraction, concurrent scans, batched inference calls. Understanding how errors cross thread boundaries is what keeps such code from silently losing failures.
