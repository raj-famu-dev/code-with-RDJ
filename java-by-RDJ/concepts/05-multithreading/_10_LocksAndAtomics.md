> 📘 Reference material drafted with Claude. Not yet learned: retype `_10_LocksAndAtomics.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Locks and Atomics

## Concept

`synchronized` is simple but limited. `java.util.concurrent` adds explicit **locks** (`ReentrantLock`, `ReadWriteLock`) and **atomic variables** that make single operations safe without a lock.

## Full Line-by-Line Breakdown

**Section 1: `ReentrantLock`.** `lock()` then `try { ... } finally { unlock(); }`. The `unlock()` **must** be in `finally`, or an exception leaves the lock held forever. Four threads x 250,000 increments: `1000000 (expected 1000000)`.

**Section 2: `tryLock`.** A holder thread owns the lock for 300 ms:

```
tryLock() while another thread holds it: false
tryLock(50 ms): false
after the holder finished, tryLock(): true
```

`tryLock` returns instead of blocking. A lock is owned by a **thread**, so the holder must be a different thread (the same thread would just re-enter).

**Section 3: `ReadWriteLock`.** Many readers at once, a writer needs exclusivity. Useful when reads far outnumber writes (measure first).

**Section 4: `AtomicInteger.incrementAndGet()`** is one indivisible step using a CPU compare-and-swap: exact `1000000` with no lock.

**Section 5: `compareAndSet(expected, new)`.**

```
compareAndSet(10, 11): true, value = 11
compareAndSet(10, 99): false, value = 11  (fails: it is 11 now)
doubled with a CAS loop: 22
```

If it fails, someone else changed it: read again and retry. `updateAndGet(v -> v * 2)` does that loop for you.

**Section 6.** `AtomicReference` swaps an object reference atomically. `LongAdder` is a counter for heavy write contention; read it with `sum()`.

## Key Rules

1. `unlock()` goes in `finally`, always.
2. Atomics make one operation safe; two atomic calls in a row are not atomic together.
3. Several variables that must change together need a lock.
4. Use `tryLock` when you cannot afford to wait forever.

## Gotchas Recap

- Forgetting `unlock()` on an error path.
- Locking and unlocking from different threads.
- Using atomics for "check then update" across two variables.

## Why This Structure Exists

Locks first because they are the closest to `synchronized`; atomics next as the lighter tool; the last-section summary tells you which to pick.
