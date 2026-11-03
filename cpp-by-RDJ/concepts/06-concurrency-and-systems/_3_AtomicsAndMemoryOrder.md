# `_3_AtomicsAndMemoryOrder.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`std::atomic<T>` makes reads, writes and read-modify-write operations on a single variable indivisible, so many threads can use a counter or flag without a mutex and without a data race. `compare_exchange` is the building block for lock-free updates: "set this to NEW only if it is still OLD". Memory orders control how other memory operations are ordered around an atomic: `relaxed` guarantees only atomicity, while `release`/`acquire` pairs let one thread safely publish data to another. Compile with `-pthread`.

## Full Line-by-Line Breakdown

### SECTION 1: ATOMIC COUNTER
Four threads each call `fetch_add(1, relaxed)` 100000 times and the total is exactly 400000. `relaxed` is enough for a plain counter because we only care about the final count, not about ordering relative to other data. The overloaded operators (`++a`, `a += 10`, `exchange`) are also atomic. The last line reports whether `atomic<int>` is always lock-free on this machine (true here). A plain `long` incremented the same way would be a data race and is described, not run.

Output from a real run:

```text
===== SECTION 1: ATOMIC COUNTER =====
4 threads x 100000 fetch_add = 400000 (expected 400000)
A plain 'long' with ++ in the same loops would be a data race (undefined behaviour); not run here.
operators work too: ++a -> 6, a += 10 -> 16, exchange(0) returned 16, now 0
std::atomic<int> is lock free on this machine: true
```

### SECTION 2: compare_exchange
`compare_exchange_strong(expected, desired)` stores `desired` only if the current value equals `expected`, and returns whether it did. When it fails, `expected` is overwritten with the actual current value (the output shows it refreshed to 20), so a retry loop can use it directly. `update_max` is a lock-free "keep the largest" built on this: reload, check, try to swap, repeat if another thread interfered. Four threads propose values up to 3999 and the maximum is exactly 3999. TRAP: `if (x.load() == 0) x.store(1);` is two separate atomic operations, so another thread can change `x` in between; use compare_exchange. `compare_exchange_weak` may fail spuriously, so use it inside a loop (as `update_max` does); `_strong` does not.

Output from a real run:

```text
===== SECTION 2: compare_exchange =====
expected 10, actual 10 -> success=true, value=20
expected 10, actual 20 -> success=false, value=20, expected was refreshed to 20
lock-free maximum over all threads = 3999 (expected 3999)
TRAP: 'if (x.load() == 0) x.store(1);' is NOT atomic as a pair; another thread can slip in between. Use compare_exchange.
compare_exchange_weak may fail spuriously (so use it in a loop); _strong does not.
```

### SECTION 3: ACQUIRE / RELEASE: PUBLISHING DATA
The producer writes ordinary data (`payload = 1234`) and then does `ready.store(true, release)`. The consumer spins on `ready.load(acquire)`. The release store and the acquire load form a pair: everything the producer wrote BEFORE the release is guaranteed visible to the consumer AFTER its acquire sees `true`. So the consumer always prints 1234. If both sides used `relaxed`, the flag would still be atomic but there would be no promise the payload write is visible: relaxed means atomicity without ordering. (That broken variant is described only; it is a data race on `payload`, so it is not run.)

Output from a real run:

```text
===== SECTION 3: ACQUIRE / RELEASE: PUBLISHING DATA =====
consumer saw payload = 1234 (guaranteed, because acquire pairs with release)
With memory_order_relaxed on both sides the flag itself stays atomic, but the payload write
would NOT be guaranteed visible: relaxed gives atomicity without ordering.
```

### SECTION 4: A SPIN LOCK FROM acquire/release
`SpinLock` is a lock built from `atomic_flag`: `test_and_set(acquire)` takes it and `clear(release)` drops it. The acquire on lock and release on unlock mean each thread sees the writes of the previous holder, so the ordinary `long protected_sum` is safe. Four threads times 20000 gives exactly 80000. The default memory order if you write nothing is `seq_cst`, the strongest and simplest; reach for relaxed/acquire/release only when you understand why. (A spin lock burns CPU while waiting; in real code prefer `std::mutex` unless you have measured a reason.)

Output from a real run:

```text
===== SECTION 4: A SPIN LOCK FROM acquire/release =====
protected_sum = 80000 (expected 80000)
lock = acquire, unlock = release: the unlock publishes this thread's writes to the next locker.
Default is memory_order_seq_cst (strongest, simplest). Reach for relaxed/acquire/release only with a reason.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `AtomicInteger`, `AtomicLong`, `AtomicReference` in `java.util.concurrent.atomic`. | `std::atomic<int>`, `std::atomic<long>`, any trivially copyable `T`. |
| `incrementAndGet()`, `compareAndSet(expect, update)`. | `fetch_add(1)` / `++`, `compare_exchange_strong(expected, desired)` (also updates `expected` on failure). |
| `volatile` gives visibility and ordering (happens-before). | `volatile` does NOT make anything thread-safe in C++. Use `std::atomic`. |
| Java Memory Model: volatile and synchronized give sequentially consistent semantics. | You choose: `seq_cst` (default), `acquire`/`release`, or `relaxed`. More power, more ways to be wrong. |
| `VarHandle` has acquire/release modes (advanced). | Standard `memory_order` arguments on every atomic call. |

## Key Rules / Gotchas Recap
- A data race on a non-atomic variable is undefined behaviour; make shared variables atomic or lock them.
- Atomic operations are individually atomic; combinations of them (`load` then `store`) are not. Use read-modify-write or compare_exchange.
- `compare_exchange` updates `expected` on failure; use `_weak` in loops.
- Relaxed = atomic but no ordering; release/acquire pairs publish data; seq_cst is the default and safest.
- `volatile` is not for threading.
- Start with `std::mutex`; go lock-free only for a clear, measured need.

## Why This Structure Exists
Counters, flags and lock-free queues are in the heart of high-throughput inference servers and network tools. Memory ordering is also where a lot of subtle concurrency bugs and security-relevant races come from, so having an accurate mental model (atomic is not the same as ordered) is valuable.
