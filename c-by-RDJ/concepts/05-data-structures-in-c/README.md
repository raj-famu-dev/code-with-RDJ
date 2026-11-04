<div align="center">

# Module 05 — Data Structures in C

![Status](https://img.shields.io/badge/Status-Completed-22C55E?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-7-7C3AED?style=for-the-badge)
![C](https://img.shields.io/badge/C-C17-A8B9CC?style=for-the-badge&logo=c&logoColor=black)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)
![Type](https://img.shields.io/badge/Type-Capstone%20Module-3B82F6?style=for-the-badge)

*Everything built from malloc: arrays, lists, tables, sorting, testing*

[Overview](#-overview) •
[Topics](#-topics) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 04](../04-files-and-systems/) · [C Lab](../../README.md)

</div>

---

## 🎯 Overview

**Focus:** the capstone module — the classic structures built with nothing but pointers and `malloc`, each proven with tests and sanitizers. This is the C twin of `java-by-RDJ/concepts/14-dsa-in-java` and `cpp-by-RDJ/project-01`: no library containers exist to lean on, so the structures *are* the curriculum. Every file follows the **oracle method** used across this repo: run seeded random operations against the structure and check the results against an independent reference.

**Exit test:** implement a dynamic array that doubles its capacity; a hash table that resizes; a `qsort` comparator that never violates strict weak ordering; and a test harness that prints `N checks, 0 failed`.

---

## 📚 Topics

| # | File | Concept | Status |
|---|------|---------|:---:|
| 1 | `_1_DynamicArray.c` | `realloc` growth, amortized O(1) append, measured copies per add | ✅ |
| 2 | `_2_LinkedList.c` | Singly then doubly linked, O(1) insert/remove with the node | ✅ |
| 3 | `_3_StackAndQueue.c` | On the linked list; on the dynamic array; overflow by design | ✅ |
| 4 | `_4_HashTable.c` | Chaining, hashing strings (djb2/FNV), load factor and resize | ✅ |
| 5 | `_5_Sorting.c` | `qsort` with comparators, plus hand-rolled quicksort and mergesort | ✅ |
| 6 | `_6_Searching.c` | `bsearch`, hand-rolled binary search, why sorted input is the contract | ✅ |
| 7 | `_7_TestingInC.c` | `assert`, a tiny harness in the repo's style (`N checks, 0 failed`), valgrind vs sanitizers | ✅ |

---

## 🔧 Run It

```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _N_Name.c && ./demo

# every file in this module under the sanitizers:
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo _N_Name.c && ./demo
```

---

## 📝 Status Note

Complete — 7 topics written and verified: dynamic array (measured 1.31 copies/push, matching the JDK's ArrayList), linked list, stack and ring-buffer queue, hash table (measured chain walks), sorting (qsort + quicksort + mergesort, verified identical), searching, and the CHECK-based test harness (105 checks, 0 failed). ASan/UBSan clean.
