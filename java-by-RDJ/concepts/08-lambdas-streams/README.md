<div align="center">

<img src="../../assets/modules/08-lambdas-streams.svg" alt="Lambdas, Streams, Optional: Functional pipelines over collections. Animated banner by Raj Patel (RDJ)." width="100%"/>

<br/>

![Status](https://img.shields.io/badge/Status-Completed-22C55E?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-8-7C3AED?style=for-the-badge)
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

*Functional pipelines over collections*

[Overview](#-overview) •
[Topics](#-topics) •
[Concept Notes](#-concept-notes) •
[Exit Test](#-exit-test) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 07](../07-file-io/) · [Java Mastery Lab](../../README.md) · [Module 09](../09-modern-java/) ➡

</div>

---

## 🎯 Overview

**Priority: NEXT.** Requires `03-collections` and `06-generics`.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic.

**Module status:** ✅ Completed: written, run and explained (written with Claude, disclosed).

**Authorship:** Written with Claude (Sonnet 5.5), then compiled and verified. The first line of every file states its origin.

## 📚 Topics

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_FunctionalInterfaces` | `Function`, `Predicate`, `Consumer`, `Supplier`, `BiFunction` | ✅ |
| 2 | `_2_LambdasAndMethodReferences` | Rewrite an anonymous class as a lambda, then as a method reference | ✅ |
| 3 | `_3_StreamBasics` | Source, intermediate, terminal operations | ✅ |
| 4 | `_4_MapFilterReduce` | `map`, `filter`, `flatMap`, `reduce`, `sorted`, `distinct`, `limit` | ✅ |
| 5 | `_5_Collectors` | `toMap`, `groupingBy`, `partitioningBy`, `joining` | ✅ |
| 6 | `_6_LazyEvaluation` | Prove laziness with `peek` and show short-circuiting | ✅ |
| 7 | `_7_OptionalDoneRight` | What `Optional` is for and where not to use it | ✅ |
| 8 | `_8_StreamsCapstone` | Employee analytics: group by department, average salary, top earners | ✅ |

## 📖 Concept Notes

A short explanation of every topic. The linked walkthrough has the full line-by-line breakdown, the traps and the gotchas.

### 1. Functional Interfaces

A **functional interface** has exactly **one abstract method**. Because there is only one thing to implement, Java lets you write it as a short **lambda**. `@FunctionalInterface` makes the compiler check the rule. `java.util.function` already has the shapes you need.

📄 [`_1_FunctionalInterfaces.java`](./_1_FunctionalInterfaces.java) · 📝 [walkthrough](./_1_FunctionalInterfaces.md)

### 2. Lambdas And Method References

A **lambda** is an inline implementation of a functional interface. A **method reference** (`Class::method`) is an even shorter form when a lambda only calls one existing method.

📄 [`_2_LambdasAndMethodReferences.java`](./_2_LambdasAndMethodReferences.java) · 📝 [walkthrough](./_2_LambdasAndMethodReferences.md)

### 3. Stream Basics

A **stream** is a pipeline that describes what to do with a sequence of values: `SOURCE -> intermediate operations -> TERMINAL operation`. It is **not a collection** (stores nothing), does **not change its source**, and can be used **once**.

📄 [`_3_StreamBasics.java`](./_3_StreamBasics.java) · 📝 [walkthrough](./_3_StreamBasics.md)

### 4. Map Filter Reduce

The everyday intermediate operations plus `reduce`. Data used: `numbers = [5, 3, 8, 3, 1, 9, 8, 2]` and `words = [stream, lambda, filter, map, reduce]`.

📄 [`_4_MapFilterReduce.java`](./_4_MapFilterReduce.java) · 📝 [walkthrough](./_4_MapFilterReduce.md)

### 5. Collectors

`collect(...)` is the terminal operation that gathers a stream into a result; a **Collector** says how. `Collectors.*` has ready-made ones. Data: six `Person` records (a record is a small class with fields and accessors such as `name()`; see `09`).

Map results are copied into `TreeMap`s so the printed order is stable (a `HashMap`'s iteration order should never be relied on).

📄 [`_5_Collectors.java`](./_5_Collectors.java) · 📝 [walkthrough](./_5_Collectors.md)

### 6. Lazy Evaluation

Intermediate operations only **describe** the pipeline; nothing runs until a terminal operation. Elements then flow through **one at a time**, and **short-circuiting** operations stop as soon as the answer is known. `peek` (a debugging tool) lets us watch.

📄 [`_6_LazyEvaluation.java`](./_6_LazyEvaluation.java) · 📝 [walkthrough](./_6_LazyEvaluation.md)

### 7. Optional Done Right

`Optional<T>` holds either one value or nothing. Its purpose is to make "this result may be absent" part of a method's **return type**, so callers cannot forget. It is a return-type tool, not a general null replacement.

📄 [`_7_OptionalDoneRight.java`](./_7_OptionalDoneRight.java) · 📝 [walkthrough](./_7_OptionalDoneRight.md)

### 8. Streams Capstone

Answer eight business questions about seven employees, **each with one pipeline**, then compare with a plain loop. Uses `groupingBy`, downstream collectors, `partitioningBy`, `flatMap`, `sorted`/`limit`, `Optional`.

📄 [`_8_StreamsCapstone.java`](./_8_StreamsCapstone.java) · 📝 [walkthrough](./_8_StreamsCapstone.md)

## 🧪 Exit Test

take one of your loop-based programs, rewrite it with streams, and say honestly whether it got more readable.

## 🚀 Run It

From the repository root (JDK 21):

```bash
cd java-by-RDJ/concepts/08-lambdas-streams
javac -d out _*.java
java -cp out _1_FunctionalInterfaces
```

`out/` is git-ignored. Swap `_1_FunctionalInterfaces` for any other `_N_Name` class to run that topic.

## 🧾 Status Note

**Key:** ✅ completed (written, run and explained in a walkthrough) · 🔄 in progress · ⬜ not started.

✅ = completed: the `.java` file and its `.md` walkthrough are written, compiled and run. Each file's first line states who wrote it.

---

<div align="center">

### 👨‍💻 Built and owned by Raj Patel (RDJ)

Computer Science undergraduate at **Florida A&M University** · Tallahassee, Florida · GitHub [`raj-famu-dev`](https://github.com/raj-famu-dev) · Instagram [`@rdj_369`](https://instagram.com/rdj_369)

This is my personal learning lab and portfolio. I build it, I maintain it, and I am accountable for what it claims.

<sub>Completed means written, run and explained in a walkthrough. These files were written with Claude (Sonnet 5.5) and say so in their first line.</sub>

⬅ [Module 07](../07-file-io/) · [Java Mastery Lab](../../README.md) · [Module 09](../09-modern-java/) ➡

**© 2026 Raj Patel (RDJ).** Released under the [MIT License](../../LICENSE).

</div>
