# `tests.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`tests.cpp` is a hand-rolled test runner for `ThreadPool`: a `CHECK` macro counts checks and failures, a `CHECK_THROWS` macro verifies exceptions, `RUN` prints PASS or FAIL per test, and `main` returns 0 only if everything passed. Concurrency tests are dangerous because a bug can freeze the test instead of failing it, so every wait that could hang uses `wait_for` with a time limit.

## Full Line-by-Line Breakdown

### The nine tests
| Test | What it proves |
|---|---|
| `test_every_task_runs_exactly_once` | 5000 tasks on 4 workers; each increments its own atomic slot; afterwards every slot is exactly 1 (none lost, none repeated) |
| `test_results_in_submission_order` | 200 tasks with uneven work (so they finish out of order); `futures[i].get()` still returns task i's result; also forwards a move-only `unique_ptr` argument |
| `test_single_worker_is_fifo` | With one worker, 100 tasks run in exactly the order they were submitted |
| `test_exception_propagates` | The exact exception type and message come out of `get()`; a `void` task works too; 100 tasks of which every tenth throws: 90 succeed, 10 fail, and the pool is still alive |
| `test_shutdown_with_pending_tasks_drains_them` | One worker is held by a blocker task (the test waits until it has *started*); 50 more tasks queue behind it (`pending() == 50`, none run yet); after the gate opens, `shutdown()` returns only after all 50 ran; submit after shutdown throws; a second `shutdown()` is harmless |
| `test_destructor_drains_pending_tasks` | Destroying the pool right after submitting 500 tasks still runs all 500 |
| `test_discard_pending_breaks_promises` | `discard_pending()` returns 10, none of the 10 ever runs, each future throws `broken_promise`, and the already-started blocker still completes |
| `test_no_deadlock_under_many_small_tasks` | (a) 1000 tiny tasks, each future waited on with a 20 s limit, sum checked; (b) 4 producer threads submit 1000 tasks each at the same time into 3 workers: 4000 ran; (c) tasks that submit further tasks, with shutdown racing them; (d) 200 pools created and destroyed in a row |
| `test_thread_count_defaults` | `ThreadPool(0)` still has at least one worker; `ThreadPool(3)` has 3 |

### The "wait until the blocker has started" trick
To make "there are pending tasks" a fact instead of a hope, the blocker task sets a promise when it starts and then waits on a gate; the test waits for that promise before queuing the rest. Without it, the worker might not have picked up the blocker yet, and the numbers would depend on timing.

### Real output
```text
Running ThreadPool tests (hardware_concurrency = 2)
[PASS] test_every_task_runs_exactly_once
[PASS] test_results_in_submission_order
[PASS] test_single_worker_is_fifo
[PASS] test_exception_propagates
[PASS] test_shutdown_with_pending_tasks_drains_them
[PASS] test_destructor_drains_pending_tasks
[PASS] test_discard_pending_breaks_promises
[PASS] test_no_deadlock_under_many_small_tasks
[PASS] test_thread_count_defaults
28 checks, 0 failed
```
The suite was run 30 times in a row in a normal build: every run printed `28 checks, 0 failed`.

## Key Differences From Java
| Java (JUnit with `ExecutorService`) | C++ here |
|---|---|
| `@Timeout` on a test | Explicit `wait_for(20s)` on the futures that could hang |
| `CountDownLatch` | `std::promise<void>` / `std::shared_future<void>` as a start signal and a gate |
| `AtomicInteger` | `std::atomic<int>` |
| `assertThrows` | `CHECK_THROWS(expr, Type)` |

## Key Rules / Gotchas Recap
- Bound every wait that could block forever, so a deadlock is a FAIL.
- Make "pending" and "running" states deterministic with a gate instead of sleeping.
- Compare against a known count (5000, 4000, 1000), not "it did not crash".
- Run the suite under ASan/UBSan and under TSan too (see the README for what TSan says here).

## Why This Structure Exists
Concurrency bugs are timing-dependent, so tests must force the interesting situations (pending tasks at shutdown, many producers, rapid create/destroy) and be repeated many times; this is the same discipline used on any queue, scheduler or connection pool.
