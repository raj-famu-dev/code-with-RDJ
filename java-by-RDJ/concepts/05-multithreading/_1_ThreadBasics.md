> 📘 Reference material drafted with Claude. Not yet learned: retype `_1_ThreadBasics.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Thread Basics

## Concept

A **thread** is an independent path of execution inside one program. Every Java program starts with one thread, `main`. Creating more lets different pieces of work run at the same time.

## Full Line-by-Line Breakdown

**Section 1: the main thread.** `Thread.currentThread().getName()` prints `main`. Your code was already running on a thread before you created any.

**Section 2: three ways to describe work.**
- A `Runnable` (the work) handed to `new Thread(runnable, "name")`. This is the preferred way: work and thread are separate things.
- A subclass `Greeter extends Thread` overriding `run()`. Works, but ties the work to the thread.
- A lambda, which is just a short `Runnable`.

**Section 3: `run()` vs `start()`: the classic mistake.**

```
Calling worker1.run() directly:
  Runnable running on thread: main
Calling worker1.start():
  Runnable running on thread: worker-1
```

`run()` is an ordinary method call on the current thread, so nothing concurrent happens (it printed `main`). `start()` asks the JVM to create a new thread, which then calls `run()` (it printed `worker-1`).

**Section 4: `join()`.** `join()` makes the calling thread wait until the other thread ends. Without it `main` could carry on before the workers finish. `worker2` and `worker3` run at the same time, so the order of their two lines can differ between runs.

**Section 5: start only once.** Calling `start()` on a finished thread throws `IllegalThreadStateException`.

**Section 6: daemon threads.** The JVM exits when the last non-daemon thread ends. A daemon thread (`setDaemon(true)`, which must come before `start()`) is a background helper. The `background` thread loops forever, yet the program still ends because it is a daemon.

**Section 7: exceptions kill only their own thread.** `boom-thread` throws; the uncaught-exception handler reports it; `main` continues.

## Key Rules

1. `start()` creates a thread; `run()` does not.
2. A thread can be started only once.
3. `join()` waits for a thread to finish.
4. Prefer a `Runnable` over extending `Thread`.
5. `setDaemon(true)` must be called before `start()`.
6. An uncaught exception ends only the thread it happened in.

## Gotchas Recap

- Calling `run()` by mistake gives a program that "works" but is single-threaded.
- Forgetting `join()` means reading results before they exist.
- Output order between concurrent threads is not guaranteed.
- Non-daemon threads you forget about keep the JVM alive.

## Why This Structure Exists

Section 3 comes before `join()` because the `run()`/`start()` mix-up is the first mistake nearly everyone makes, and seeing `main` printed instead of `worker-1` makes it impossible to forget.
