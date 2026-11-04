<div align="center">

# Module 03 — Structs & Modularity

![Status](https://img.shields.io/badge/Status-Completed-22C55E?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-8-7C3AED?style=for-the-badge)
![C](https://img.shields.io/badge/C-C17-A8B9CC?style=for-the-badge&logo=c&logoColor=black)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)
![Type](https://img.shields.io/badge/Type-Concept%20Practice-3B82F6?style=for-the-badge)

*Structs, typedef, unions, enums, function pointers, headers and linking*

[Overview](#-overview) •
[Topics](#-topics) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 02](../02-pointers-and-memory/) · [C Lab](../../README.md) · [Module 04](../04-files-and-systems/) ➡

</div>

---

## 🎯 Overview

**Focus:** how C organizes data and code without classes. `struct` is C's record, `typedef` names it, function pointers are C's polymorphism (and the heart of `qsort`'s comparator), and the header/`extern`/`static`/linker model is what `#include` actually means. Struct padding and packing are covered because they are real bugs in binary files and network code.

**Exit test:** design a `struct` with a function-pointer "method table"; explain why `sizeof(struct)` exceeds the sum of its fields; split a small program into a `.h` and two `.c` files and link them.

---

## 📚 Topics

| # | File | Concept | Status |
|---|------|---------|:---:|
| 1 | `_1_Structs.c` | Definition, designated initializers, assignment semantics | ✅ |
| 2 | `_2_Typedef.c` | Naming types, opaque structs (the C "private class") | ✅ |
| 3 | `_3_NestedAndArrayOfStructs.c` | Composition in C: structs in structs, arrays of records | ✅ |
| 4 | `_4_PassingStructs.c` | By value (copy) vs by pointer, `const struct *`, returning pointers safely | ✅ |
| 5 | `_5_Unions.c` | Overlapping storage, type punning and its (UB) edges, tagged unions | ✅ |
| 6 | `_6_EnumsAndBitfields.c` | Enums as ints, bitfields for packed flags, `sizeof` surprises | ✅ |
| 7 | `_7_FunctionPointers.c` | Callbacks, `qsort` comparators, dispatch tables — C's polymorphism | ✅ |
| 8 | `_8_HeadersAndLinking.c` | Include guards, `extern`, `static` linkage, multi-file builds, the linker's job | ✅ |

---

## 🔧 Run It

```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _N_Name.c && ./demo

# topic 8 spans multiple files:
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo module.c main.c && ./demo
```

---

## 📝 Status Note

Complete — 8 topics written and verified, including the multi-file topic 8 (`_8_counter.h` / `_8_counter.c` / `_8_HeadersAndLinking.c`), which builds with both files on the link line.
