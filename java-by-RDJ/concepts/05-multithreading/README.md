# 05 · Multithreading and Concurrency

**Priority: NOW (after 03 and 04).** The hardest folder in the repo. Reproduce every bug before fixing it.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic.

## Planned files

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_ThreadBasics` | `Thread` vs `Runnable`; what is the difference between `start()` and `run()`? | ⬜ |
| 2 | `_2_RunnableAndCallable` | How do you get a result or an exception back from another thread? | ⬜ |
| 3 | `_3_ThreadLifecycle` | NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED; `join`, `sleep`, `interrupt` | ⬜ |
| 4 | `_4_RaceConditions` | Make `count++` lose updates across threads and show the wrong total | ⬜ |
| 5 | `_5_Synchronized` | Fix the race with `synchronized`; method vs block; what is being locked? | ⬜ |
| 6 | `_6_VolatileAndMemoryModel` | Visibility vs atomicity; a stop-flag bug that `volatile` fixes | ⬜ |
| 7 | `_7_WaitNotify` | Producer-consumer using `wait`/`notifyAll`; why a `while` loop, not `if` | ⬜ |
| 8 | `_8_ExecutorService` | Thread pools, `submit`, `shutdown`, `awaitTermination` | ⬜ |
| 9 | `_9_FutureAndCompletableFuture` | Chaining async work, combining results, handling errors | ⬜ |
| 10 | `_10_LocksAndAtomics` | `ReentrantLock`, `ReadWriteLock`, `AtomicInteger`, compare with `synchronized` | ⬜ |
| 11 | `_11_ConcurrentCollections` | `ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue` | ⬜ |
| 12 | `_12_Deadlock` | Create a real deadlock, then fix it with lock ordering | ⬜ |
| 13 | `_13_VirtualThreads` | Java 21 virtual threads: what problem they solve and when they do not help | ⬜ |
| 14 | `_14_ConcurrencyCapstone` | Process many files concurrently and compare sequential vs parallel timing | ⬜ |

## Traps to hit on purpose
- Calling `run()` and wondering why nothing is concurrent
- Forgetting `executor.shutdown()` so the program never exits
- Swallowing `InterruptedException`
- Two locks taken in opposite order by two threads
- Assuming `volatile` makes `count++` safe (it does not)

## Exit test (answer from memory)
1. Explain a race condition using your own `_4` output.
2. `synchronized` vs `volatile` vs `AtomicInteger`: which fixes what, and which does not?
3. Name the four conditions for deadlock and break one of them in code.
4. Why would you use a thread pool instead of creating a thread per task?

Do not mark this folder ✅ until all 14 files and all 14 `.md` files are committed.
