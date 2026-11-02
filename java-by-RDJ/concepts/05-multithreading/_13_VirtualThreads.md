> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Virtual Threads (Java 21)

## Concept

A normal **platform thread** wraps an operating-system thread: heavy, so a machine supports only thousands. A **virtual thread** is managed by the JVM and is very light, so hundreds of thousands are possible. When a virtual thread blocks (sleep, network, file), the JVM parks it and lets the underlying OS thread run another one.

## Full Line-by-Line Breakdown

**Section 2: creating them.**

```
inside: isVirtual = true
inside: isVirtual = false
virtual threads are always daemon threads: true
```

`Thread.ofVirtual().name(..).start(..)`, `Thread.ofPlatform()`, and the shortcut `Thread.startVirtualThread(..)`.

**Section 3: one virtual thread per task.** `Executors.newVirtualThreadPerTaskExecutor()` makes a new virtual thread for every task. Do not pool them. 2,000 tasks that each block for 200 ms:

```
2000 tasks x 200 ms of blocking, virtual threads: finished 2000, about 235 ms
```

**Section 4: the same style of work on 50 platform threads.** 500 tasks need 10 rounds of 200 ms:

```
500 tasks x 200 ms of blocking, 50 platform threads: finished 500, about 2016 ms
```

These timings are measurements from this machine in one run and will differ on yours. The comparison is about **blocking** work only.

**Section 5: what they are for.** Many tasks that mostly **wait** (network, database, files). **Not** for CPU-bound work: if tasks compute all the time, you are limited by cores and virtual threads give no speed-up.

**Section 6: things to know.** Do not pool; in Java 21 a long `synchronized` block around a blocking call can "pin" the virtual thread to its OS thread, so prefer `ReentrantLock` there; thread-locals get costly at massive scale.

## Key Rules

1. One virtual thread per task, never pooled.
2. Good for blocking I/O; no help for CPU-bound work.
3. They are always daemon threads.
4. Keep blocking code simple and blocking: that is the point.

## Gotchas Recap

- Expecting a speed-up on number crunching.
- `synchronized` around blocking calls (pinning) in Java 21.
- Treating the timing numbers above as universal.

## Why This Structure Exists

The side-by-side run turns the abstract claim "virtual threads scale" into something you measured, with the limits stated right next to it.
