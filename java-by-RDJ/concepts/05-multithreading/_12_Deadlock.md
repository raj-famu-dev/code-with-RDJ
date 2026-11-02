> 📘 Reference material drafted with Claude. Not yet learned: retype `_12_Deadlock.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Deadlock

## Concept

A **deadlock** is when thread 1 holds lock A and wants B while thread 2 holds B and wants A. Both wait forever. It needs all four conditions: mutual exclusion, hold and wait, no preemption, circular wait. Break any one and deadlock is impossible.

## Full Line-by-Line Breakdown

**Section 2: causing one safely.** Each thread takes its first lock, then both meet at a `CyclicBarrier` so each holds its first lock before either asks for the second. That makes the deadlock happen **every time**. Both threads are **daemons**, so the demo can never keep the JVM alive.

**Section 3: detecting it.** `ThreadMXBean.findDeadlockedThreads()` asks the JVM which threads are in a lock cycle (a `jstack <pid>` thread dump shows the same in a real app). The program polls for up to 3 seconds:

```
DEADLOCK detected, 2 threads involved:
  deadlock-t1 is BLOCKED, waiting for a lock owned by deadlock-t2
  deadlock-t2 is BLOCKED, waiting for a lock owned by deadlock-t1
```

**Section 4: fix 1, same lock order.** Both threads take `a` then `b` (a fresh pair, since the demo's locks are still stuck). Whoever gets `a` first finishes; the other waits its turn. This breaks "circular wait".

```
ordered-t1 got both locks (same order as everyone else)
ordered-t2 got both locks (same order as everyone else)
ordered threads finished: true
```

(The line order of the two threads can swap between runs.)

**Section 5: fix 2, `tryLock` with a timeout.** The threads ask in **opposite** orders, but if the second lock is not available in 50 ms they release the first, pause for a random few milliseconds and retry. This breaks "hold and wait":

```
tryLock threads finished: true, completed work: 2 of 2
```

**Section 6: checklist.** Fewer locks, one global order, no calling unknown code while holding a lock, `tryLock` when order cannot be guaranteed. Related: **livelock** (threads keep reacting, no progress) and **starvation** (one thread never gets a turn).

## Key Rules

1. Take multiple locks in one global order.
2. Never call callbacks or overridable methods while holding a lock.
3. Use `tryLock` with a timeout when order cannot be guaranteed.
4. Deadlock is not recoverable inside the JVM: the stuck threads stay stuck.

## Gotchas Recap

- A deadlock may happen only under rare timing, so it can hide for months.
- Random backoff is needed, otherwise two `tryLock` threads can retry in lockstep (livelock).
- Never run a deadlock demo with non-daemon threads.

## Why This Structure Exists

Cause it, detect it, then fix it two ways: the only reliable way to remember it is to have watched the JVM report it.
