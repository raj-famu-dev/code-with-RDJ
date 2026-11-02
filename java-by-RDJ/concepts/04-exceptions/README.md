<div align="center">

<img src="../../assets/modules/04-exceptions.svg" alt="Exceptions: try, catch, finally, custom exceptions. Animated banner by Raj Patel (RDJ)." width="100%"/>

<br/>

![Status](https://img.shields.io/badge/Status-Reference%20Material-0EA5E9?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-8-7C3AED?style=for-the-badge)
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

*try, catch, finally, custom exceptions*

[Overview](#-overview) •
[Topics](#-topics) •
[Traps to Hit on Purpose](#-traps-to-hit-on-purpose) •
[Exit Test](#-exit-test) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 03](../03-collections/) · [Java Mastery Lab](../../README.md) · [Module 05](../05-multithreading/) ➡

</div>

---

## 🎯 Overview

**Priority: NOW.** Project 03 (bank system) cannot be built properly without this.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic.

**Module status:** 📘 Reference material: compiled and run, not yet counted as mine.


## 📚 Topics

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_ExceptionHandlingBasics` | try / catch / finally, multi-catch, `throw` basics. **`.java` is your own code; the `.md` was drafted by Claude** | 📘 |
| 2 | `_2_CheckedVsUnchecked` | What does the compiler force on you, and why was the line drawn there? | 📘 |
| 3 | `_3_ThrowAndThrows` | Declaring vs triggering; how an exception travels up the call stack | 📘 |
| 4 | `_4_CustomExceptions` | When to extend `Exception` vs `RuntimeException`; adding fields like an error code | 📘 |
| 5 | `_5_TryWithResources` | `AutoCloseable`, close order, suppressed exceptions | 📘 |
| 6 | `_6_ExceptionChaining` | Wrapping with a cause, `getCause()`, why dropping the cause loses the real bug | 📘 |
| 7 | `_7_FinallyGotchas` | What happens if `finally` contains a `return`, or itself throws? | 📘 |
| 8 | `_8_ExceptionsCapstone` | Validated input pipeline with a custom exception hierarchy | 📘 |

## 🪤 Traps to Hit on Purpose
- Empty `catch` block that hides a bug
- Catching `Exception` or `Throwable` when a specific type is meant
- `return` inside `finally` swallowing an exception
- Rethrowing a new exception without the original cause
- Catch order: general type above specific type (compile error, see why)

## 🧪 Exit Test

*(answer from memory)*
1. Checked vs unchecked: give two examples of each and defend the design choice for your own custom exception.
2. What is printed, and why, for a method with `try { return 1; } finally { System.out.println("x"); }`?
3. When should a method catch an exception, and when should it let it propagate?

## 🚀 Run It

From the repository root (JDK 21):

```bash
cd java-by-RDJ/concepts/04-exceptions
javac -d out _*.java
java -cp out _2_CheckedVsUnchecked
```

`out/` is git-ignored. Swap `_2_CheckedVsUnchecked` for any other `_N_Name` class to run that topic. `_1_ExceptionHandlingBasics` is interactive (it reads from the keyboard), so run it from a terminal.

## 🧾 Status Note

**Key:** ✅ complete and understood by me · 📘 reference added (compiled and run) · 🔄 in progress · ⬜ not started.

📘 = reference file and walkthrough committed (compiled and run). Do not mark a row ✅ until you have retyped the file, broken it on purpose, and rewritten its `.md` in your own words.

---

<div align="center">

### 👨‍💻 Built and owned by Raj Patel (RDJ)

Computer Science undergraduate at **Florida A&M University** · Tallahassee, Florida · GitHub [`raj-famu-dev`](https://github.com/raj-famu-dev)

This is my personal learning lab and portfolio. I build it, I maintain it, and I am accountable for what it claims.

<sub>`_1`'s `.java` is my own code. Everything else here was drafted with Claude as reference and says so; I count a topic as mine (✅) only after I retype it, break it on purpose and rewrite its walkthrough in my own words.</sub>

⬅ [Module 03](../03-collections/) · [Java Mastery Lab](../../README.md) · [Module 05](../05-multithreading/) ➡

**© 2026 Raj Patel (RDJ).** Released under the [MIT License](../../LICENSE).

</div>
