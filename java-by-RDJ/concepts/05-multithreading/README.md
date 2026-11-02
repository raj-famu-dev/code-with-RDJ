<div align="center">

<img src="../../assets/modules/05-multithreading.svg" alt="Multithreading: Threads, locks, races, executors. Animated banner by Raj Patel (RDJ)." width="100%"/>

<br/>

![Status](https://img.shields.io/badge/Status-Reference%20Material-0EA5E9?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-14-7C3AED?style=for-the-badge)
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

*Threads, locks, races, executors*

[Overview](#-overview) •
[Topics](#-topics) •
[Traps to Hit on Purpose](#-traps-to-hit-on-purpose) •
[Exit Test](#-exit-test) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 04](../04-exceptions/) · [Java Mastery Lab](../../README.md) · [Module 06](../06-generics/) ➡

</div>

---

## 🎯 Overview

**Priority: NOW (after 03 and 04).** The hardest folder in the repo. Reproduce every bug before fixing it.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic.

**Module status:** 📘 Reference material: compiled and run, not yet counted as mine.


## 📚 Topics

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_ThreadBasics` | `Thread` vs `Runnable`; what is the difference between `start()` and `run()`? | 📘 |
| 2 | `_2_RunnableAndCallable` | How do you get a result or an exception back from another thread? | 📘 |
| 3 | `_3_ThreadLifecycle` | NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED; `join`, `sleep`, `interrupt` | 📘 |
| 4 | `_4_RaceConditions` | Make `count++` lose updates across threads and show the wrong total | 📘 |
| 5 | `_5_Synchronized` | Fix the race with `synchronized`; method vs block; what is being locked? | 📘 |
| 6 | `_6_VolatileAndMemoryModel` | Visibility vs atomicity; a stop-flag bug that `volatile` fixes | 📘 |
| 7 | `_7_WaitNotify` | Producer-consumer using `wait`/`notifyAll`; why a `while` loop, not `if` | 📘 |
| 8 | `_8_ExecutorService` | Thread pools, `submit`, `shutdown`, `awaitTermination` | 📘 |
| 9 | `_9_FutureAndCompletableFuture` | Chaining async work, combining results, handling errors | 📘 |
| 10 | `_10_LocksAndAtomics` | `ReentrantLock`, `ReadWriteLock`, `AtomicInteger`, compare with `synchronized` | 📘 |
| 11 | `_11_ConcurrentCollections` | `ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue` | 📘 |
| 12 | `_12_Deadlock` | Create a real deadlock, then fix it with lock ordering | 📘 |
| 13 | `_13_VirtualThreads` | Java 21 virtual threads: what problem they solve and when they do not help | 📘 |
| 14 | `_14_ConcurrencyCapstone` | Process many files concurrently and compare sequential vs parallel timing | 📘 |

## 🪤 Traps to Hit on Purpose
- Calling `run()` and wondering why nothing is concurrent
- Forgetting `executor.shutdown()` so the program never exits
- Swallowing `InterruptedException`
- Two locks taken in opposite order by two threads
- Assuming `volatile` makes `count++` safe (it does not)

## 🧪 Exit Test

*(answer from memory)*
1. Explain a race condition using your own `_4` output.
2. `synchronized` vs `volatile` vs `AtomicInteger`: which fixes what, and which does not?
3. Name the four conditions for deadlock and break one of them in code.
4. Why would you use a thread pool instead of creating a thread per task?

## 🚀 Run It

From the repository root (JDK 21):

```bash
cd java-by-RDJ/concepts/05-multithreading
javac -d out _*.java
java -cp out _1_ThreadBasics
```

`out/` is git-ignored. Swap `_1_ThreadBasics` for any other `_N_Name` class to run that topic.

## 🧾 Status Note

**Key:** ✅ complete and understood by me · 📘 reference added (compiled and run) · 🔄 in progress · ⬜ not started.

📘 = reference file and walkthrough committed (compiled and run; race and deadlock demos are timing-dependent, so their numbers differ per run). Do not mark a row ✅ until you have retyped the file, broken it on purpose, and rewritten its `.md` in your own words.

---

<div align="center">

### 👨‍💻 Built and owned by Raj Patel (RDJ)

Computer Science undergraduate at **Florida A&M University** · Tallahassee, Florida · GitHub [`raj-famu-dev`](https://github.com/raj-famu-dev)

This is my personal learning lab and portfolio. I build it, I maintain it, and I am accountable for what it claims.

<sub>The reference files here were drafted with Claude and say so in their first line. I count a topic as mine (✅) only after I retype it, break it on purpose and rewrite its walkthrough in my own words.</sub>

⬅ [Module 04](../04-exceptions/) · [Java Mastery Lab](../../README.md) · [Module 06](../06-generics/) ➡

**© 2026 Raj Patel (RDJ).** Released under the [MIT License](../../LICENSE).

</div>
