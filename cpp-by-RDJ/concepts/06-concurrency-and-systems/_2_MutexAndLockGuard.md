# `_2_MutexAndLockGuard.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
When two threads touch the same data and at least one writes, you have a data race, which is undefined behaviour in C++. A `std::mutex` provides mutual exclusion: only the thread holding the lock may touch the data. RAII wrappers (`lock_guard`, `unique_lock`, `scoped_lock`) lock in the constructor and unlock in the destructor, so the lock is released on every exit path including exceptions. `scoped_lock` locks several mutexes together and avoids deadlock. Compile with `-pthread`.

## Full Line-by-Line Breakdown

### SECTION 1: lock_guard AND A DETERMINISTIC TOTAL
`SafeCounter::increment` locks a mutex with `std::lock_guard`, increments, and unlocks automatically at the end of the scope. Four threads each add 50000, and the total is always exactly 200000. The result is deterministic because every `++value_` happens while holding the mutex.

WHAT THE UNLOCKED VERSION WOULD DO (described only, not run): if `increment` were just `++value_` with no lock, `++` is really three steps (read, add, write back). Two threads can both read 7 and both write 8, losing an update, so the final total would usually be LESS than 200000 and would differ from run to run. Worse, a data race is undefined behaviour, so the compiler is allowed to assume it never happens and the program has no guaranteed behaviour at all. This file never runs that version, so its output does not depend on a race. You can check such code with `-fsanitize=thread`.

Output from a real run:

```text
===== SECTION 1: lock_guard AND A DETERMINISTIC TOTAL =====
4 threads x 50000 increments = 200000 (expected 200000)
The result is the same every run because each ++value_ happens while holding the mutex.
(The UNLOCKED version is described in the walkthrough; it is a data race and is not run here.)
```

### SECTION 2: unique_lock
`std::unique_lock` is a more flexible lock. It can be released early with `unlock()` and re-acquired with `lock()`; `owns_lock()` reports the state; the destructor unlocks only if it still owns the lock. `std::defer_lock` constructs it WITHOUT locking, and `try_lock()` attempts without blocking. The last check starts a second thread because calling `try_lock` on a `std::mutex` you already hold from the SAME thread is undefined behaviour (that is the TRAP); from another thread it correctly returns `false` while `main` holds the lock. `unique_lock` is also what `condition_variable::wait` requires.

Output from a real run:

```text
===== SECTION 2: unique_lock =====
owns_lock while inside: true
owns_lock after unlock(): false
shared = 2
defer_lock owns_lock: false
try_lock succeeded because nobody holds the mutex
try_lock from another thread while main holds the mutex: false
TRAP: locking a std::mutex you already hold in the same thread is undefined behaviour (usually a hang).
```

### SECTION 3: scoped_lock AND DEADLOCK AVOIDANCE
Two accounts, two threads, opposite directions. `transfer` locks both mutexes with `std::scoped_lock lock(from.m, to.m)`, which uses a deadlock-avoidance algorithm, so argument order does not matter. After 20000 transfers each way the balances return to 1000 each and the total is 2000. TRAP (described): with two separate `lock_guard`s (lock `from` then lock `to`), thread 1 can hold A waiting for B while thread 2 holds B waiting for A, and both wait forever. The rules to avoid deadlock: lock multiple mutexes at once with `scoped_lock`, or always lock in one agreed global order, and never call unknown code while holding a lock.

Output from a real run:

```text
===== SECTION 3: scoped_lock AND DEADLOCK AVOIDANCE =====
alice=1000 bob=1000 total=2000 (opposite-direction transfers did not deadlock)
TRAP: with two separate lock_guards (lock from, then lock to), thread 1 can hold A and wait for B
      while thread 2 holds B and waits for A: a deadlock. scoped_lock(a, b) locks both atomically.
Other rule: if you must lock several mutexes by hand, always lock them in one global order.
```

### SECTION 4: KEEP CRITICAL SECTIONS SMALL
Good mutex code holds locks for as short a time as possible. Each worker builds its string outside the lock and takes the lock only for the single `push_back`. The order of the log entries depends on scheduling, so the program prints only the count (4), which is stable.

Output from a real run:

```text
===== SECTION 4: KEEP CRITICAL SECTIONS SMALL =====
log has 4 entries (order depends on scheduling, so we do not print it)
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `synchronized (obj) { ... }` or `synchronized` methods; the lock is released automatically. | `std::lock_guard<std::mutex> lock(m);` the destructor releases it (RAII). Mutex and data are separate objects, you must keep the pairing disciplined. |
| `ReentrantLock` with `lock()`/`unlock()` in try/finally; reentrant. | `std::mutex` is NOT reentrant (relocking is undefined behaviour); `std::recursive_mutex` exists but is a design smell. |
| `tryLock()` on ReentrantLock. | `try_lock()` on the mutex or `std::unique_lock` with `std::try_to_lock`. |
| Lock several monitors in a fixed order by convention. | `std::scoped_lock(a, b)` does deadlock-safe multi-locking for you. |
| Racy code gives stale/odd values but is memory-safe. | A data race is undefined behaviour: not just wrong numbers, but anything. |
| `ConcurrentHashMap`, `AtomicInteger` in `java.util.concurrent`. | No concurrent containers in the standard library; you protect normal containers with your own mutex. |

## Key Rules / Gotchas Recap
- Shared data that is written must be protected by a mutex (or be atomic); reading while another thread writes is also a race.
- Always use RAII locks, never call `m.lock()` / `m.unlock()` by hand in normal code.
- `lock_guard` for simple scopes, `unique_lock` for flexibility (condition variables, early unlock), `scoped_lock` for multiple mutexes.
- Do not lock a `std::mutex` twice in one thread.
- Keep critical sections small; do slow work outside.
- A mutex only protects data if EVERY access goes through it; make the data private to a class.
- Use ThreadSanitizer (`-fsanitize=thread`) to find races.

## Why This Structure Exists
Parallel pipelines in AI services (shared caches, metrics, request queues) and security tools (shared result sets in a scanner) need correct locking. Data races are also a real source of security bugs (time-of-check/time-of-use), so knowing exactly what a lock does and does not guarantee is core systems knowledge.
