<div align="center">

<img src="../../assets/modules/14-dsa-in-java.svg" alt="Data Structures and Algorithms: Built from scratch, checked against the JDK. Animated banner by Raj Patel (RDJ)." width="100%"/>

<br/>

![Status](https://img.shields.io/badge/Status-Reference%20Material-0EA5E9?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-8-7C3AED?style=for-the-badge)
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

*Built from scratch, checked against the JDK*

[Overview](#-overview) •
[Topics](#-topics) •
[Algorithms to Cover](#-algorithms-to-cover) •
[Problem Log](#-problem-log) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 13](../13-design-patterns/) · [Java Mastery Lab](../../README.md) · [Module 15](../15-spring-boot/) ➡

</div>

---

## 🎯 Overview

**Priority: RUNS IN PARALLEL, 30 minutes a day.** Implement the structures yourself with no `java.util` collections.

Convention: one `_N_Name.java` plus one `_N_Name.md` per structure (with Big-O of every operation in the `.md`).

**Module status:** 📘 Reference material: compiled and run, not yet counted as mine.


## 📚 Topics
| # | File | Status |
|---|---|:---:|
| 1 | `_1_DynamicArray` | 📘 |
| 2 | `_2_LinkedList` (singly, then doubly) | 📘 |
| 3 | `_3_StackAndQueue` | 📘 |
| 4 | `_4_HashMapWithChaining` | 📘 |
| 5 | `_5_BinarySearchTree` | 📘 |
| 6 | `_6_MinHeap` | 📘 |
| 7 | `_7_GraphBfsDfs` | 📘 |
| 8 | `_8_Trie` | 📘 |

Every `.md` has a Big-O table, and every `.java` checks its structure against the matching `java.util` class on thousands of seeded random operations (the JDK class is used **only** as the reference in `main`, never inside the structure).

## 🧭 Algorithms to Cover
Binary search and variants, merge sort, quicksort, two pointers, sliding window, recursion and backtracking, dynamic programming (knapsack, LIS, edit distance), Dijkstra, topological sort, union-find.

**Status: ⬜ not written yet.** Only BFS, DFS and topological sort appear so far (inside `_7_GraphBfsDfs`). The rest of this list is still open.

## 📒 Problem Log
Keep a [`problems.md`](./problems.md) in this folder: date, problem, link, topic, attempts, time, what went wrong. The count in this file is the only number you are allowed to quote.

## 🚀 Run It

From the repository root (JDK 21):

```bash
cd java-by-RDJ/concepts/14-dsa-in-java
javac -d out _*.java
java -cp out _1_DynamicArray
```

`out/` is git-ignored. Swap `_1_DynamicArray` for any other `_N_Name` class to run that topic.

## 🧾 Status Note

**Key:** ✅ complete and understood by me · 📘 reference added (compiled and run) · 🔄 in progress · ⬜ not started.

📘 = reference file and walkthrough committed (compiled and run). Do not mark a row ✅ until you have retyped the file, broken it on purpose, and rewritten its `.md` in your own words.

---

<div align="center">

### 👨‍💻 Built and owned by Raj Patel (RDJ)

Computer Science undergraduate at **Florida A&M University** · Tallahassee, Florida · GitHub [`raj-famu-dev`](https://github.com/raj-famu-dev)

This is my personal learning lab and portfolio. I build it, I maintain it, and I am accountable for what it claims.

<sub>The reference files here were drafted with Claude and say so in their first line. I count a topic as mine (✅) only after I retype it, break it on purpose and rewrite its walkthrough in my own words.</sub>

⬅ [Module 13](../13-design-patterns/) · [Java Mastery Lab](../../README.md) · [Module 15](../15-spring-boot/) ➡

**© 2026 Raj Patel (RDJ).** Released under the [MIT License](../../LICENSE).

</div>
