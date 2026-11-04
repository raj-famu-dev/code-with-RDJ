<div align="center">

# Module 01 — C Basics

![Status](https://img.shields.io/badge/Status-Completed-22C55E?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-9-7C3AED?style=for-the-badge)
![C](https://img.shields.io/badge/C-C17-A8B9CC?style=for-the-badge&logo=c&logoColor=black)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)
![Type](https://img.shields.io/badge/Type-Concept%20Practice-3B82F6?style=for-the-badge)

*Compilation, types, operators, control flow, loops, arrays, strings, functions, stdio*

[Overview](#-overview) •
[Topics](#-topics) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [C Lab](../../README.md) · [Module 02](../02-pointers-and-memory/) ➡

</div>

---

## 🎯 Overview

**Focus:** the C compilation pipeline and the language's core: statically typed, no classes, no GC, no bounds checks. Every topic pairs with a walkthrough `.md` and contrasts with Java and Python — the two languages already in this repo — so each concept reinforces all three.

**Exit test:** explain what `gcc` does at each of its four stages; predict a program's output including its undefined behavior; explain why `int` overflow isn't an exception in C.

---

## 📚 Topics

| # | File | Concept | Status |
|---|------|---------|:---:|
| 1 | `_1_HelloWorldAndCompilation.c` | The gcc pipeline (preprocess → compile → assemble → link); flags: `-std=c17 -Wall -Wextra -Wpedantic` | ✅ |
| 2 | `_2_VariablesAndTypes.c` | Fixed-width types (`stdint.h`), `sizeof`, `limits.h`, signed vs unsigned | ✅ |
| 3 | `_3_OperatorsAndCasting.c` | Integer promotion, truncation, and **signed overflow is undefined behavior** (UBSan demo) | ✅ |
| 4 | `_4_ControlFlow.c` | `if`/`else`, `switch` with fall-through semantics | ✅ |
| 5 | `_5_Loops.c` | `for`/`while`/`do-while`, `break`/`continue` | ✅ |
| 6 | `_6_Arrays.c` | Fixed-size arrays, initializer lists, **no bounds checking** | ✅ |
| 7 | `_7_StringsAndStringH.c` | `char` arrays and `'\0'`, `string.h`, why `gets()` is banned (and `fgets()` isn't) | ✅ |
| 8 | `_8_FunctionsAndPrototypes.c` | Prototypes, pass-by-value only, the header/source split | ✅ |
| 9 | `_9_FormattedIO.c` | `printf`/`scanf` specifiers, return values you must check, buffer pitfalls | ✅ |

---

## 🔧 Run It

```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _N_Name.c && ./demo
```

---

## 📝 Status Note

Complete — 9 topics written and verified: each `.c` compiles with zero warnings (`-std=c17 -Wall -Wextra -Wpedantic`), runs with exit 0, and has a paired `.md` walkthrough. Module 02 and 05 files also verified clean under AddressSanitizer + UndefinedBehaviorSanitizer.
