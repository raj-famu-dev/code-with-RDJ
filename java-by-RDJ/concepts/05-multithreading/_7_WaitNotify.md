> 📘 Reference material drafted with Claude. Not yet learned: retype `_7_WaitNotify.java`, break it on purpose, then rewrite this walkthrough in your own words.

# wait() and notify()

## Concept

When a thread needs a condition that another thread must create (a consumer needs data), it should **wait** instead of looping and checking (busy waiting burns CPU). The producer **notifies** when something changes.

## Full Line-by-Line Breakdown

**The rules (Section 2).** `wait`, `notify`, `notifyAll` are methods of `Object`. You must hold that object's lock. `wait()` **releases** the lock while sleeping and re-takes it before returning. The demo proves the first rule:

```
Caught IllegalMonitorStateException: wait() needs the lock first
```

**`BoundedBuffer`.** A queue limited to `capacity` items.
- `put`: `while (items.size() == capacity) wait();` then add and `notifyAll()`.
- `take`: `while (items.isEmpty()) wait();` then remove and `notifyAll()`.
- Both methods are `synchronized`, so the lock and the wait/notify belong to the same object.

**Producer-consumer (Section 3).** The producer puts 1..8 into a buffer of size 3, then `-1` as a "poison value" meaning "no more data". The consumer takes until it sees `-1`:

```
consumed in order: [1, 2, 3, 4, 5, 6, 7, 8]
```

The two threads interleave differently on each run, but the consumer always receives the values in the same order.

**Section 4: `while`, not `if`.** After waking you must re-check the condition, because of spurious wakeups and because another thread may have taken the item first.

**Section 5: `notify` vs `notifyAll`.** `notify()` wakes one arbitrary waiter, which may be the wrong kind (a producer woken when only a consumer can progress), and the program can hang. `notifyAll()` is the safe default.

## Key Rules

1. Call `wait`/`notify` only while holding that object's lock.
2. Always wait inside a `while` loop that re-checks the condition.
3. Prefer `notifyAll()`.
4. `wait()` releases the lock; `sleep()` does not.

## Gotchas Recap

- `if` instead of `while` causes rare, hard-to-reproduce bugs.
- Waiting on one object but locking another gives `IllegalMonitorStateException`.
- A missed notification can hang forever: always have a timeout or poison value in real code.

## Why This Structure Exists

Learning this by hand shows what `BlockingQueue` (`_11`) does internally. In real code you should use the ready-made class.
