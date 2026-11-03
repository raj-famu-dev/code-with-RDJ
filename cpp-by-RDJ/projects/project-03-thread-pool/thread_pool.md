# `thread_pool.hpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A thread pool starts a fixed number of worker threads once and feeds them tasks through a shared queue, instead of creating a thread per task. `ThreadPool` does this with `std::jthread`, a `std::mutex`-guarded queue and a condition variable. `submit` hands back a `std::future`, so the caller gets either the task's result or the exception it threw, and shutting the pool down finishes the queued work first.

## Full Line-by-Line Breakdown

### Members and construction
One mutex protects the task queue and the `accepting_` flag. `std::condition_variable_any cv_` lets idle workers sleep. `workers_` (a vector of `std::jthread`) is declared last so it is destroyed first. The constructor starts `threads` workers, each running `worker_loop` with a `std::stop_token`. A request for 0 threads means "ask the hardware"; because `hardware_concurrency()` may itself return 0, the pool never has fewer than one worker. Copying is deleted: threads and mutexes cannot be copied.

### `submit`: from any callable to a future
`submit(f, args...)` wraps `f(args...)` in a lambda that owns decayed copies of the function and arguments (a `std::tuple` applied with `std::apply`, so move-only arguments like `std::unique_ptr` work). That lambda becomes a `std::packaged_task<Result()>`: a callable that runs the function and stores the result **or any exception** in a shared state. `get_future()` returns the matching `std::future<Result>` before the task is queued. Because `packaged_task` can only be moved but `std::function` needs copyable callables, the task sits behind a `std::shared_ptr` and the queue stores a small lambda that calls it. Under the lock, `submit` checks `accepting_` (after shutdown it throws `std::runtime_error`) and pushes; `notify_one` wakes one sleeping worker.

```text
===== SECTION 1: submit returns a future; results are read in submission order =====
squares of 1..8 via 4 workers: 1 4 9 16 25 36 49 64
```

(The squares come back as `1 4 9 ... 64` in submission order no matter which worker finished first: each future is tied to its own task.)

### `worker_loop`: sleep, take, run
```text
cv_.wait(lock, stop, [this] { return !tasks_.empty(); });
if (tasks_.empty()) return;
```
This `condition_variable_any` overload sleeps until the predicate is true **or a stop is requested**, re-checking the predicate under the lock to survive spurious wake-ups. It returns with an empty queue only when stopping, which is the exit condition: *stop requested and nothing left to drain*. The task is moved out of the queue while the lock is held, but **run after the lock is released**, so other workers keep taking tasks while this one works.

### Exceptions
A task that throws does not unwind the worker: `packaged_task` catches it and stores it. `future.get()` rethrows the same exception object in the caller, with its original type. The worker simply moves on to the next task (Section 2 of the demo and `test_exception_propagates`).

```text
===== SECTION 2: an exception thrown inside a task is rethrown by future.get() =====
caught in the caller: task failed on purpose
the pool still works afterwards: 7
```

### `shutdown()`: graceful by design
Under the lock it clears `accepting_`, so any later `submit` throws. It then calls `request_stop()` on every `jthread` (which also wakes sleepers) and joins them. Workers keep running until the queue is empty, so **every task submitted before shutdown still runs**. A separate `shutdown_mutex_` stops two threads from joining the same thread. Calling it twice is harmless, and the destructor calls it, so a pool going out of scope never leaves threads behind.

```text
===== SECTION 3: shutdown() lets queued tasks finish =====
100 tasks submitted, pool destroyed immediately, tasks completed = 100
```

### `discard_pending()`
The opposite policy: swap the queue's contents out under the lock and destroy them outside it. A task destroyed without running makes its promise broken, so its future's `get()` throws `std::future_error` with `broken_promise`. Tasks a worker has already started are not affected. Together with `shutdown()` this gives "finish everything" or "drop what has not started".

## Key Differences From Java
| Java (`ExecutorService`) | C++ (`ThreadPool`) |
|---|---|
| `submit(Callable)` returns `Future<T>` | `submit(f, args...)` returns `std::future<T>` for any callable, including lambdas with move-only arguments |
| A task's exception is wrapped in `ExecutionException` by `Future.get()` | `future.get()` rethrows the original exception, same type |
| `shutdown()` finishes queued tasks; `shutdownNow()` interrupts and drops them | `shutdown()` finishes queued tasks; `discard_pending()` drops the unstarted ones (running tasks are never interrupted) |
| You must call `shutdown()` or threads keep the JVM alive | The destructor shuts down, and `std::jthread` joins automatically |
| `Thread.interrupt()` | `std::stop_token` / `request_stop()`: cooperative, wakes `condition_variable_any` waits |
| Everything is a `Runnable`/`Callable` object | Templates deduce the return type; `std::function` is used only inside the queue |

## Key Rules / Gotchas Recap
- Always wait on a condition variable with a predicate, under the mutex.
- Run the task outside the lock.
- Never wait on a future from inside a task of a small pool: if all workers are waiting on tasks still in the queue, nothing can run (deadlock). The tests submit nested work without waiting for it.
- A discarded or abandoned task gives its future a `broken_promise`, not a hang.
- A future from `submit` can be dropped; the task still runs and the exception (if any) is simply discarded.
- `std::thread::hardware_concurrency()` is a hint and may be 0.

## Why This Structure Exists
Thread pools sit under web servers, build tools, data pipelines and inference services: they bound how many threads exist and move work between them. The same pieces (a locked queue, a condition variable, futures, graceful shutdown) are also where deadlocks and data races are born, so getting each one right in a small class is the best preparation for debugging them in a big one.
