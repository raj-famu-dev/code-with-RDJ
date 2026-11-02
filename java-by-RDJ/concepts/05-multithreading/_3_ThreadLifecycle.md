> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Thread Lifecycle

## Concept

At any moment a thread is in exactly one of six states, readable with `getState()`. The program provokes each state on purpose and prints it.

## Full Line-by-Line Breakdown

**The helper `waitForState`.** Threads change state on their own schedule, so instead of a guessed `sleep`, it polls `getState()` every 5 ms for up to 2 seconds.

**The six states and how each is produced:**

| State | How the program produces it |
|---|---|
| `NEW` | created, `start()` not called |
| `RUNNABLE` | a busy loop checking an `AtomicBoolean` |
| `TIMED_WAITING` | `Thread.sleep(500)` |
| `BLOCKED` | `main` holds `LOCK`, so the new thread cannot enter `synchronized (LOCK)` |
| `WAITING` | `LOCK.wait()` with no timeout |
| `TERMINATED` | after the thread finished |

Real output:

```
before start():  NEW
after finishing: TERMINATED
busy loop:       RUNNABLE
in sleep(500):   TIMED_WAITING
lock is taken:   BLOCKED
in wait():       WAITING
```

**Interrupts (Section 7).**

```
  woke up with InterruptedException, flag now: false
  after restoring, flag: true
```

`interrupt()` does not kill a thread: it sets a flag, and blocking calls like `sleep()` react by throwing `InterruptedException`. Catching it **clears** the flag, so good code restores it with `Thread.currentThread().interrupt()`.

**Section 8: `join(50)`** waits at most 50 ms; the thread is still alive afterwards (`true`).

## Key Rules

1. `BLOCKED` = waiting for a `synchronized` lock. `WAITING` = waiting for `notify`/`join`/`park`. They are different.
2. `interrupt()` is a request, not a kill.
3. After catching `InterruptedException`, restore the flag (or rethrow).
4. Never use a guessed `sleep` to wait for a state: poll or use proper signalling.

## Gotchas Recap

- Swallowing `InterruptedException` with an empty catch hides a cancellation request.
- `sleep()` and `wait()` are different: only `wait()` releases the lock.
- `getState()` is a snapshot; it may already be out of date when you read it.

## Why This Structure Exists

Each state gets its own tiny experiment, so the names stop being a memorised list and become something you have actually observed.
