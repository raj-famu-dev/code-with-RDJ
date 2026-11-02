> 📘 Reference material drafted with Claude. Not yet learned: retype `_6_VolatileAndMemoryModel.java`, break it on purpose, then rewrite this walkthrough in your own words.

# volatile and the Java Memory Model

## Concept

Two different problems hide inside "threads share data":

- **Visibility**: when one thread writes a variable, will another *see* it? Threads may use cached copies, and the JIT compiler may reorder or reuse reads.
- **Atomicity**: can a multi-step operation (`value++`) be interrupted halfway?

`volatile` fixes **visibility** (and ordering). It does **not** give atomicity.

## Full Line-by-Line Breakdown

**Section 2: a volatile stop flag (correct use).** The worker loops on `while (!volatileStop)`. After 100 ms `main` sets the flag; the worker sees it and ends:

```
  volatile worker saw the flag and stopped
volatile worker still alive? false
```

**Section 3: volatile does not make `++` atomic.** Two threads each add 200,000 to a volatile counter. Two runs:

```
volatile counter: expected 400000, got 400000
volatile counter: expected 400000, got 392725
```

The first run was lucky. Updates can still be lost; the fix is `synchronized` or `AtomicInteger` (`_10`).

**Section 4: the same stop flag without volatile.**

```
plain worker is STILL RUNNING: it never saw plainStop = true
```

On this JVM the worker never noticed the change. This outcome is **allowed but not guaranteed**: another JVM or CPU may print "stopped". The worker is a daemon so the program still exits. Do not rely on this experiment giving the same result everywhere.

**Section 5: happens-before.** The rules that define visibility: a volatile write precedes later reads of it; an unlock precedes the next lock of the same monitor; `start()` precedes the started thread's code; a thread's actions precede another thread's `join()` returning.

## Key Rules

1. Use `volatile` for simple flags written by one thread and read by others.
2. Never use `volatile` for counters or any read-modify-write.
3. Without a happens-before relationship, another thread may never see your change.
4. `synchronized` gives visibility as well as mutual exclusion.

## Gotchas Recap

- "It works on my machine" proves nothing about memory-model bugs.
- `volatile` on a reference makes the *reference* visible, not the contents of the object it points to.
- A volatile int is still not safe to increment.

## Why This Structure Exists

Visibility and atomicity are separated first because confusing them is the most common misunderstanding of `volatile`. The non-volatile demo is deliberately labelled non-deterministic and made safe with a daemon thread.
