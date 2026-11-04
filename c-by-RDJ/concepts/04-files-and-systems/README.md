<div align="center">

# Module 04 — Files & Systems

![Status](https://img.shields.io/badge/Status-Completed-22C55E?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-8-7C3AED?style=for-the-badge)
![C](https://img.shields.io/badge/C-C17-A8B9CC?style=for-the-badge&logo=c&logoColor=black)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)
![Type](https://img.shields.io/badge/Type-Concept%20Practice-3B82F6?style=for-the-badge)

*stdio file I/O, binary formats, errors, argv, the preprocessor, make*

[Overview](#-overview) •
[Topics](#-topics) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 03](../03-structs-and-modularity/) · [C Lab](../../README.md) · [Module 05](../05-data-structures-in-c/) ➡

</div>

---

## 🎯 Overview

**Focus:** programs that survive a restart. `stdio`'s buffered file model, text vs binary modes, error handling through `errno` and return codes (C has no exceptions), command-line arguments, the preprocessor (macros done safely), and building multi-file projects with `make`. This module is what makes `project-01-grade-manager-c` possible — persistence, arguments and a build.

**Exit test:** write a program that reads a CSV file, reports each failure mode precisely (missing file, bad line, short line), writes a corrected binary file, and builds with a Makefile exposing `make`, `make test` and `make sanitize`.

---

## 📚 Topics

| # | File | Concept | Status |
|---|------|---------|:---:|
| 1 | `_1_FileOpenAndClose.c` | `fopen`/`fclose`, modes (`r`, `w`, `a`, `b`), checking for failure | ✅ |
| 2 | `_2_TextIO.c` | `fgets` + `sscanf` (the safe pattern), `fprintf`, buffering | ✅ |
| 3 | `_3_BinaryIO.c` | `fread`/`fwrite`, struct packing, endianness, magic headers | ✅ |
| 4 | `_4_ErrnoAndExitCodes.c` | `errno`, `perror`/`strerror`, exit codes as the CLI contract | ✅ |
| 5 | `_5_CommandLineArguments.c` | `argc`/`argv`, option parsing, stdin/stdout as files | ✅ |
| 6 | `_6_PreprocessorAndMacros.c` | `#define` pitfalls, `#ifdef`, include guards, `static inline` in headers | ✅ |
| 7 | `_7_MakeAndBuilds.c` | A real Makefile: targets, dependencies, `make clean` (matching `cpp-by-RDJ` projects) | ✅ |
| 8 | `_8_FlexibleArrayMembers.c` | The `struct { size_t n; T data[]; }` pattern for malloc'd records | ✅ |

---

## 🔧 Run It

```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _N_Name.c && ./demo
make && ./demo        # topic 7 onward
```

---

## 📝 Status Note

Complete — 8 topics written and verified. The Makefile in topic 7 mirrors `cpp-by-RDJ`'s projects (`make -f _7_Makefile`, `test`, `sanitize`, `clean`) so the two labs feel like one system.

---

<div align="center">

<sub>Built and owned by [Raj Patel (RDJ)](https://github.com/raj-famu-dev) — Computer Science @ **Florida A&M University** · Tallahassee, Florida · [Instagram @rdj_369](https://instagram.com/rdj_369)</sub>

[⬅ c-by-RDJ](../../README.md) · [Repository home](../../../README.md)

</div>
