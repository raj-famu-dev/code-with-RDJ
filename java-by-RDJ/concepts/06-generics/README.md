<div align="center">

<img src="../../assets/modules/06-generics.svg" alt="Generics: Type parameters, bounds, wildcards. Animated banner by Raj Patel (RDJ)." width="100%"/>

<br/>

![Status](https://img.shields.io/badge/Status-Completed-22C55E?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-6-7C3AED?style=for-the-badge)
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

*Type parameters, bounds, wildcards*

[Overview](#-overview) •
[Topics](#-topics) •
[Concept Notes](#-concept-notes) •
[Exit Test](#-exit-test) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 05](../05-multithreading/) · [Java Mastery Lab](../../README.md) · [Module 07](../07-file-io/) ➡

</div>

---

## 🎯 Overview

**Priority: NEXT.** Finish `03` to `05` first. Generics make the collections you learned in `03` make sense.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic.

**Module status:** ✅ Completed: written, run and explained (written with Claude, disclosed).

**Authorship:** Written with Claude (Sonnet 5.5), then compiled and verified. The first line of every file states its origin.

## 📚 Topics

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_GenericClasses` | Write your own `Box<T>` and `Pair<A, B>`; why not just use `Object`? | ✅ |
| 2 | `_2_GenericMethods` | Type inference, `static <T> ...` | ✅ |
| 3 | `_3_BoundedTypes` | `<T extends Comparable<T>>` and writing a generic `max` | ✅ |
| 4 | `_4_Wildcards` | `?`, `? extends T`, `? super T`; the PECS rule with one example of each | ✅ |
| 5 | `_5_TypeErasure` | What disappears at runtime, why generic arrays are restricted | ✅ |
| 6 | `_6_GenericsCapstone` | Your own generic `Stack<T>` and `Queue<T>` | ✅ |

## 📖 Concept Notes

A short explanation of every topic. The linked walkthrough has the full line-by-line breakdown, the traps and the gotchas.

### 1. Generic Classes

A generic class has a **type parameter** (`<T>`): a placeholder filled in by whoever uses the class. `Box<String>` means "a Box where T is String". It gives you reuse (one class for every type) **and** compile-time type safety (no casts).

📄 [`_1_GenericClasses.java`](./_1_GenericClasses.java) · 📝 [walkthrough](./_1_GenericClasses.md)

### 2. Generic Methods

A method can have its own type parameter, declared **before the return type**: `static <T> T firstOf(List<T> items)`. It works for any type, even inside a class that is not generic.

📄 [`_2_GenericMethods.java`](./_2_GenericMethods.java) · 📝 [walkthrough](./_2_GenericMethods.md)

### 3. Bounded Types

A plain `<T>` tells you nothing about `T` except that it is an `Object`, so you cannot compare or add two `T`s. A **bound** (`<T extends Comparable<T>>`) narrows `T` so that useful methods become available, and the compiler enforces it.

📄 [`_3_BoundedTypes.java`](./_3_BoundedTypes.java) · 📝 [walkthrough](./_3_BoundedTypes.md)

### 4. Wildcards

Even though `Dog` is an `Animal`, a `List<Dog>` is **not** a `List<Animal>`. Wildcards (`?`) let a method accept a family of generic types safely.

📄 [`_4_Wildcards.java`](./_4_Wildcards.java) · 📝 [walkthrough](./_4_Wildcards.md)

### 5. Type Erasure

Generics exist only for the **compiler**. After checking your types, the compiler removes them: `List<String>` becomes plain `List` in the `.class` file, with casts inserted where you read. This kept old non-generic code compatible, and it explains most generics restrictions.

📄 [`_5_TypeErasure.java`](./_5_TypeErasure.java) · 📝 [walkthrough](./_5_TypeErasure.md)

### 6. Generics Capstone

Build your own generic `Stack<T>` (last in, first out) and `Queue<T>` (first in, first out) on a chain of linked nodes, with no `java.util` collections inside. It pulls together generic classes, generic nested types, bounds and PECS wildcards.

📄 [`_6_GenericsCapstone.java`](./_6_GenericsCapstone.java) · 📝 [walkthrough](./_6_GenericsCapstone.md)

## 🧪 Exit Test

explain PECS and why `List<Object>` is not a supertype of `List<String>`.

## 🚀 Run It

From the repository root (JDK 21):

```bash
cd java-by-RDJ/concepts/06-generics
javac -d out _*.java
java -cp out _1_GenericClasses
```

`out/` is git-ignored. Swap `_1_GenericClasses` for any other `_N_Name` class to run that topic.

## 🧾 Status Note

**Key:** ✅ completed (written, run and explained in a walkthrough) · 🔄 in progress · ⬜ not started.

✅ = completed: the `.java` file and its `.md` walkthrough are written, compiled and run. Each file's first line states who wrote it.

---

<div align="center">

### 👨‍💻 Built and owned by Raj Patel (RDJ)

Computer Science undergraduate at **Florida A&M University** · Tallahassee, Florida · GitHub [`raj-famu-dev`](https://github.com/raj-famu-dev) · Instagram [`@rdj_369`](https://instagram.com/rdj_369)

This is my personal learning lab and portfolio. I build it, I maintain it, and I am accountable for what it claims.

<sub>Completed means written, run and explained in a walkthrough. These files were written with Claude (Sonnet 5.5) and say so in their first line.</sub>

⬅ [Module 05](../05-multithreading/) · [Java Mastery Lab](../../README.md) · [Module 07](../07-file-io/) ➡

**© 2026 Raj Patel (RDJ).** Released under the [MIT License](../../LICENSE).

</div>
