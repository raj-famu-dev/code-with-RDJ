<div align="center">

# Module 02 — Pointers & Memory

![Status](https://img.shields.io/badge/Status-Not%20Started-F59E0B?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-8-7C3AED?style=for-the-badge)
![C](https://img.shields.io/badge/C-C17-A8B9CC?style=for-the-badge&logo=c&logoColor=black)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)
![Type](https://img.shields.io/badge/Type-Concept%20Practice-3B82F6?style=for-the-badge)

*Pointers, pointer arithmetic, the stack vs the heap, malloc/free, sanitizers*

[Overview](#-overview) •
[Topics](#-topics) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 01](../01-basics/) · [C Lab](../../README.md) · [Module 03](../03-structs-and-modularity/) ➡

</div>

---

## 🎯 Overview

**Focus:** the module that C exists to teach. Pointers as addresses, the difference between automatic (stack) and dynamic (heap) storage, and the discipline of `malloc`/`free` ownership. The C++ lab's `02-pointers-and-memory` is the direct sequel — same six bug classes, caught by the same sanitizers — but here there is no smart pointer to rescue you.

**Exit test:** draw the memory state of a program (stack, heap, pointers) at a given line; diagnose a use-after-free from a raw ASan report; state who owns and who frees every allocation in a snippet.

---

## 📚 Topics

| # | File | Concept | Status |
|---|------|---------|:---:|
| 1 | `_1_PointersAndAddresses.c` | `&` and `*`, `NULL`, pointer size, multiple indirection | ⬜ |
| 2 | `_2_PointerArithmetic.c` | Element-sized steps, one-past-the-end legality, `ptrdiff_t` | ⬜ |
| 3 | `_3_ArraysAndPointers.c` | Array-to-pointer decay, `a[i]` as `*(a+i)`, 2-D arrays vs pointer-to-pointer | ⬜ |
| 4 | `_4_StringsAsCharPointers.c` | String literals (read-only!) vs `char` arrays, ownership of strings | ⬜ |
| 5 | `_5_StackVsHeap.c` | `malloc`/`calloc`/`realloc`/`free`, automatic vs dynamic lifetime | ⬜ |
| 6 | `_6_MemoryBugsAndSanitizers.c` | The classic bugs — use-after-free, heap overflow, leak, double-free — each caught by ASan/UBSan, then fixed | ⬜ |
| 7 | `_7_ConstAndVoidPointers.c` | `const` correctness in C, `void*` casting rules, why C has no `new` | ⬜ |
| 8 | `_8_MemoryOwnershipPatterns.c` | Who frees: cleanup paths, the `goto cleanup` idiom, documenting ownership in APIs | ⬜ |

---

## 🔧 Run It

```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _N_Name.c && ./demo

# every file in this module, additionally, under the sanitizers:
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo _N_Name.c && ./demo
```

---

## 📝 Status Note

Scaffold only — designed, not written. This module is the prerequisite for `project-02-hash-table-c` and the direct foundation of the C++ lab's memory module.
