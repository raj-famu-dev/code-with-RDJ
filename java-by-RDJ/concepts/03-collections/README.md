<div align="center">

<img src="../../assets/modules/03-collections.svg" alt="Collections Framework: List, Set, Map, Queue and the cost of each. Animated banner by Raj Patel (RDJ)." width="100%"/>

<br/>

![Status](https://img.shields.io/badge/Status-Reference%20Material-0EA5E9?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-13-7C3AED?style=for-the-badge)
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

*List, Set, Map, Queue and the cost of each*

[Overview](#-overview) •
[Topics](#-topics) •
[Traps to Hit on Purpose](#-traps-to-hit-on-purpose) •
[Exit Test](#-exit-test) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 02](../02-oop/) · [Java Mastery Lab](../../README.md) · [Module 04](../04-exceptions/) ➡

</div>

---

## 🎯 Overview

**Priority: NOW.** Everything after this folder (streams, Spring, the projects) is built on collections.

Convention: one `_N_Name.java` (sectioned, runnable) plus one `_N_Name.md` (line-by-line walkthrough) per topic, same as `01-basics` and `02-oop`.

**Module status:** 📘 Reference material: compiled and run, not yet counted as mine.


## 📚 Topics

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_CollectionsFrameworkOverview` | Where do `List`, `Set`, `Queue`, `Map` sit in the hierarchy, and why is `Map` not a `Collection`? | 📘 |
| 2 | `_2_ArrayList` | How does it grow? Cost of add at end, add at index 0, `get(i)`, `remove(i)`? | 📘 |
| 3 | `_3_LinkedList` | Why is `get(i)` slow? When is it genuinely faster than `ArrayList`? | 📘 |
| 4 | `_4_HashSet` | How do `hashCode` and `equals` (see `02-oop/_12`) decide what counts as a duplicate? | 📘 |
| 5 | `_5_LinkedHashSetAndTreeSet` | What ordering does each guarantee, and what does `TreeSet` require of its elements? | 📘 |
| 6 | `_6_HashMap` | `put`, `get`, `getOrDefault`, `merge`, `computeIfAbsent`, iterating `entrySet()` | 📘 |
| 7 | `_7_HashMapInternals` | Buckets, collisions, load factor, resizing, long buckets turning into trees | 📘 |
| 8 | `_8_LinkedHashMapAndTreeMap` | Insertion order vs access order vs sorted keys, and the navigation methods | 📘 |
| 9 | `_9_QueueDequePriorityQueue` | FIFO vs LIFO, `ArrayDeque` vs `Stack`, how a `PriorityQueue` orders elements | 📘 |
| 10 | `_10_Iterators` | `Iterator.remove()`, fail-fast behavior, reproduce `ConcurrentModificationException` | 📘 |
| 11 | `_11_ComparableVsComparator` | Natural vs custom ordering, `Comparator.comparing(...).thenComparing(...)` | 📘 |
| 12 | `_12_UtilityAndImmutableCollections` | `Collections` helpers, `List.of` vs `Arrays.asList` vs `unmodifiableList` | 📘 |
| 13 | `_13_CollectionsCapstone` | Word-frequency counter, LRU cache, and a ranked leaderboard in one program | 📘 |

## 🪤 Traps to Hit on Purpose

*(write a failing example, then fix it)*
- Modifying a list while looping over it
- Using a mutable object as a `HashMap` key, then changing it
- `equals` overridden without `hashCode`
- `List<Integer>.remove(1)` vs `remove(Integer.valueOf(1))`
- `Arrays.asList(...)` is fixed-size; `List.of(...)` is immutable

## 🧪 Exit Test

*(answer from memory, no code open)*
1. Walk through what happens inside `HashMap.put("a", 1)` step by step.
2. Pick the right collection for: unique names in insertion order; top-K scores; undo history; cache with eviction.
3. Give the time complexity of the main operations of `ArrayList`, `LinkedList`, `HashMap`, `TreeMap`, `PriorityQueue`.
4. Why does `ConcurrentModificationException` exist?

## 🚀 Run It

From the repository root (JDK 21):

```bash
cd java-by-RDJ/concepts/03-collections
javac -d out _*.java
java -cp out _1_CollectionsFrameworkOverview
```

`out/` is git-ignored. Swap `_1_CollectionsFrameworkOverview` for any other `_N_Name` class to run that topic.

## 🧾 Status Note

**Key:** ✅ complete and understood by me · 📘 reference added (compiled and run) · 🔄 in progress · ⬜ not started.

📘 = reference file and walkthrough committed (compiled and run). Do not mark a row ✅ until you have retyped the file, broken it on purpose, and rewritten its `.md` in your own words.

---

<div align="center">

### 👨‍💻 Built and owned by Raj Patel (RDJ)

Computer Science undergraduate at **Florida A&M University** · Tallahassee, Florida · GitHub [`raj-famu-dev`](https://github.com/raj-famu-dev)

This is my personal learning lab and portfolio. I build it, I maintain it, and I am accountable for what it claims.

<sub>The reference files here were drafted with Claude and say so in their first line. I count a topic as mine (✅) only after I retype it, break it on purpose and rewrite its walkthrough in my own words.</sub>

⬅ [Module 02](../02-oop/) · [Java Mastery Lab](../../README.md) · [Module 04](../04-exceptions/) ➡

**© 2026 Raj Patel (RDJ).** Released under the [MIT License](../../LICENSE).

</div>
