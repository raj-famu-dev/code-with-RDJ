# `_1_ThreadsAndJoin.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`std::thread` starts a new thread of execution running a function you give it. You must either `join()` it (wait for it to finish) or `detach()` it (let it run on its own) before the `std::thread` object is destroyed; otherwise the program calls `std::terminate`. Arguments are COPIED into the thread, so to share a variable by reference you must wrap it in `std::ref`. `std::jthread` (C++20) fixes the biggest pitfall by joining automatically and supporting cooperative cancellation. Compile with `-pthread`.

## Full Line-by-Line Breakdown

### SECTION 1: START AND JOIN
A `std::thread` starts running its callable immediately. `joinable()` is true while the thread object owns a running or finished-but-unjoined thread, and `join()` blocks until it ends; afterwards `joinable()` is false. Printing goes through a mutex-protected `say()` helper so lines from different threads cannot interleave characters. (`hardware_concurrency()` is not printed because it differs per machine.)

Output from a real run:

```text
===== SECTION 1: START AND JOIN =====
joinable before join: true
hello from a worker thread
joinable after join:  false
hardware_concurrency is machine-specific, so not printed; calling it returns a hint only.
```

### SECTION 2: MANY THREADS, DETERMINISTIC RESULT
Eight threads each fill one slot of a `std::vector<int>`; each thread writes only to its own element, so there is no shared mutable state and no data race, and the result `0 1 4 ... 49` is the same every time. Threads are collected in a `std::vector<std::thread>` and all joined. The vector is passed with `std::ref` (next section explains why).

Output from a real run:

```text
===== SECTION 2: MANY THREADS, DETERMINISTIC RESULT =====
squares: 0 1 4 9 16 25 36 49
```

### SECTION 3: PASSING ARGUMENTS, std::ref TRAP
TRAP: `std::thread` copies (or moves) its arguments into internal storage, then calls the function with them as rvalues. A function taking `int&` therefore cannot bind to the copy: `std::thread t(add_to, total, 5)` does not compile (verified: "std::thread arguments must be invocable after conversion to rvalues"). `std::ref(total)` wraps a real reference, so the thread changes `total` (5). A by-value lambda capture changes only the thread's private copy (`copy_target` stays 0). Moving a string into a lambda capture empties the original (`size 0`). Also take care that the referenced variable outlives the thread.

Output from a real run:

```text
===== SECTION 3: PASSING ARGUMENTS, std::ref TRAP =====
with std::ref the original changed: total = 5
by-value capture changes only the thread's own copy: copy_target = 0
moved into the thread
message after being moved into the lambda has size 0 (moved-from)
```

### SECTION 4: FORGOT TO JOIN (opt-in)
A `std::thread` that is still joinable when its destructor runs calls `std::terminate`. This is skipped by default. With `--forget-join` the program creates a thread and leaves scope without joining; the real run printed `terminate called without an active exception` and exited with code 134 (abort). Because this demo is deliberate, it is only reachable through the flag.

Output from a real run:

```text
===== SECTION 4: FORGOT TO JOIN (opt-in) =====
Destroying a joinable std::thread calls std::terminate (the program aborts).
(skipped; run with --forget-join to see it)
```

### SECTION 5: DETACH
`detach()` cuts the thread loose: the object is no longer joinable (`false`) and nobody can wait for it through the thread object. The demo only touches a variable owned by `main` and has `main` spin until an atomic flag says the detached thread finished. TRAP: if the function owning the variables returns (or `main` ends) while a detached thread still uses them, the thread reads destroyed memory. Prefer `join` or `jthread`.

Output from a real run:

```text
===== SECTION 5: DETACH =====
joinable after detach: false
main waited using an atomic flag; detached thread finished.
TRAP: if main (or the function owning the variables) returns while a detached thread still uses them,
      the thread touches destroyed memory. Prefer join, or jthread, over detach.
```

### SECTION 6: std::jthread
`std::jthread` joins in its destructor, so leaving the scope never terminates the program; the demo sets `jt_value = 42` in the thread and reads it after the scope, which is safe because the destructor's join happens first. A `jthread` lambda can take a `std::stop_token`; `request_stop()` sets it and the loop exits cleanly (cooperative cancellation: the thread must check the token itself).

Output from a real run:

```text
===== SECTION 6: std::jthread =====
after the scope ended, the jthread had finished and set jt_value = 42
stoppable jthread saw the stop request and exited cleanly
jthread = thread + automatic join + cooperative stop_token.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `new Thread(runnable).start()`; `t.join()`. | `std::thread t(f, args...)` starts immediately; `t.join()`. |
| An unjoined thread is harmless; the JVM exits when all non-daemon threads end. | An unjoined, undetached `std::thread` destructor calls `std::terminate`. `jthread` joins for you. |
| Daemon threads: `t.setDaemon(true)`. | `t.detach()`; you must keep everything it touches alive. |
| Lambdas capture effectively-final variables; objects are shared by reference. | Capture mode is your choice: by value copies, by reference shares (and can dangle). |
| Thread arguments are references to objects; no `std::ref` equivalent. | Arguments are copied; pass `std::ref(x)` to share. |
| `Thread.interrupt()` and `isInterrupted()`. | `jthread` plus `std::stop_token` / `request_stop()`; cooperative like interrupts. |
| `ExecutorService` thread pools are the usual choice. | No standard thread pool in C++20; use `std::async`, or roll/borrow a pool. |

## Key Rules / Gotchas Recap
- Every `std::thread` must be joined or detached exactly once before destruction; prefer `std::jthread`.
- Thread arguments are copied; use `std::ref` to pass by reference, and make sure the referent outlives the thread.
- Threads may share data only if access is synchronized (mutex, atomics) or each thread touches different data.
- Do not rely on output ordering between threads.
- Detached threads must never touch data that can die first.
- Compile with `-pthread` (and consider `-fsanitize=thread` while developing).

## Why This Structure Exists
AI engineering workloads (data loading, batching, parallel inference servers) and security tools (scanners, fuzzers, packet processors) are all concurrent. Understanding thread lifetimes and argument passing is the foundation under every higher-level concurrency tool in C++.
