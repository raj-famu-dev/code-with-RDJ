> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# synchronized

## Concept

Every Java object has a built-in lock (a **monitor**). Only one thread at a time can hold it. `synchronized` makes a thread take the lock before entering a block; others wait. It also makes changes made inside visible to the next thread that takes the same lock.

## Full Line-by-Line Breakdown

**The counters.**
- `UnsafeCounter`: the broken version from `_4`.
- `MethodLockCounter`: `synchronized` on the method locks `this`.
- `BlockLockCounter`: `synchronized (lock)` on a private `final Object`, so only the needed code is locked and outsiders cannot lock your lock.
- `static synchronized incrementStatic()`: locks the `Class` object, shared by all instances.
- `WrongLockCounter`: `synchronized (new Object())` locks a new object every call, so nobody ever waits. It compiles and looks protected, but is not.

**Output (one run):**

```
unsafe:          expected 1000000, got 981921  (can be less; varies per run)
synchronized method: 1000000
synchronized block:  1000000
static synchronized: 1000000
wrong lock:      expected 1000000, got 742341  (can be less: no real protection; varies per run)
  outer() holds the lock
  inner() enters the SAME lock again: no deadlock
```

The three correct versions are exact every time. The unsafe and wrong-lock versions vary (on another run `wrong lock` happened to give 1,000,000, which proves nothing).

**Reentrancy.** `outer()` calls `inner()`, both `synchronized` on `this`. A thread that holds a lock may take it again, otherwise this would deadlock itself.

**`hammer(op, threads, times)`** is a small helper that runs one operation from several threads and joins them.

## Key Rules

1. Threads exclude each other only if they use the **same** lock object.
2. Instance method locks `this`; static method locks the class; a block locks whatever you name.
3. Use a private final lock object for blocks.
4. Intrinsic locks are reentrant.
5. Keep locked sections short; never hold a lock during slow I/O.

## Gotchas Recap

- Locking a different object each time protects nothing.
- Two `Counter` objects have separate locks.
- Reads need the same lock as writes, otherwise they may see stale data (`get()` is synchronized for that reason).
- Over-locking turns a "multithreaded" program into a sequential one.

## Why This Structure Exists

Three correct forms plus one plausible-looking wrong one: the wrong one is the real lesson, because it is the mistake that ships to production.
