<div align="center">

# 🧩 c-by-RDJ

### C17, pointers, and manual memory — the language underneath everything else in this repo

![C](https://img.shields.io/badge/C-C17-A8B9CC?style=for-the-badge&logo=c&logoColor=black)
![Compiler](https://img.shields.io/badge/Compiler-GCC%2013-77AA99?style=for-the-badge)
![Focus](https://img.shields.io/badge/Focus-Systems%20Foundations-7C3AED?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Legal%20Labs%20Only-DC2626?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Scaffold%20(Design%20Complete)-F59E0B?style=for-the-badge)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![University](https://img.shields.io/badge/Florida%20A%26M%20University-Computer%20Science-F58025?style=for-the-badge)
![Location](https://img.shields.io/badge/Tallahassee-FL-E8618C?style=for-the-badge)
![Instagram](https://img.shields.io/badge/Instagram-%40rdj_369-C13584?style=for-the-badge&logo=instagram&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

*No garbage collector. No classes. No safety net — just you, the heap, and the sanitizer.*

[About](#-about) •
[The Goal](#-the-goal) •
[Progress](#-progress) •
[Structure](#-structure) •
[Method](#-method) •
[Run It](#-run-it-yourself) •
[Integrity](#-integrity) •
[Progress Log](#-progress-log)

</div>

---

## 📌 About

This is the C lab: **C17 fundamentals, arrays, pointers, manual memory management, structs, file I/O, and data structures built from nothing but `malloc`.**

It exists for one reason — everything else in this repo sits on top of C's world:
- Java and Python hide memory behind a runtime and a GC; C makes you manage every byte yourself.
- The C++ lab already teaches RAII and smart pointers; this lab is the layer *underneath* — where `delete` doesn't exist and `free()` is a discipline, not a keyword.
- Operating systems, kernels, and the runtimes of Java, Python and C themselves are written in C. Reading C fluently is reading the foundations.

**Status: scaffold.** The curriculum is fully designed — 5 modules, 40 topics, 2 project starters, every module folder with its README and topic list — but **no code is written yet**. Each file will be added with the same conventions as the rest of this repo (paired source + walkthrough, disclosure header, tag header, sanitizer-clean builds).

---

## 🎯 The Goal

**Working fluency in C17**, proven by artifacts:

1. Explain pointers, arrays and the stack/heap distinction without hand-waving — and debug all three classic memory bugs (use-after-free, buffer overflow, leak) from a real sanitizer report.
2. Build a dynamic array, linked list, stack, queue and hash table from scratch — no libraries — and prove them with tests and sanitizers.
3. Read and modify a multi-file C project: headers, `extern`, `static`, Makefiles.
4. Port a complete Java application (the grade manager) to idiomatic C, with file persistence.

---

## 📊 Progress

| Module | Topics | Status |
|---|:-:|:---:|
| [`concepts/01-basics`](./concepts/01-basics) | 9 | ⬜ Not started |
| [`concepts/02-pointers-and-memory`](./concepts/02-pointers-and-memory) | 8 | ⬜ Not started |
| [`concepts/03-structs-and-modularity`](./concepts/03-structs-and-modularity) | 8 | ⬜ Not started |
| [`concepts/04-files-and-systems`](./concepts/04-files-and-systems) | 8 | ⬜ Not started |
| [`concepts/05-data-structures-in-c`](./concepts/05-data-structures-in-c) | 7 | ⬜ Not started |

| Project | Status |
|---|:---:|
| [`projects/project-01-grade-manager-c`](./projects/project-01-grade-manager-c) | ⬜ Not started |
| [`projects/project-02-hash-table-c`](./projects/project-02-hash-table-c) | ⬜ Not started |

**Totals: 0 of 40 topics written · 0 of 2 projects complete.**

---

## 📂 Structure

- **[`concepts/`](./concepts)**: one topic per file pair — a runnable `_N_Name.c` and a matching `_N_Name.md` explaining it line by line (same format as `java-by-RDJ`, `python-by-RDJ` and `cpp-by-RDJ`).
- **[`projects/`](./projects)**: complete programs with a Makefile and tests, combining several modules.

Every concept file will follow the established repo conventions:

```c
// Tags: #C #Pointers #MemoryManagement #Malloc | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Authorship disclosed.
```

---

## 🧪 Method

The same method as every other lab here — **write, run, break, explain, ship** — with one C-specific addition, **sanitizer-first**:

1. **Write** the smallest complete example of the concept.
2. **Run** it with `gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g`.
3. **Break it** — deliberately trigger the failure (the C++ lab's memory-safety lab is the model: bug, sanitizer report, fix).
4. **Read the sanitizer output** — ASan and UBSan reports are a skill, not an error message to paste.
5. **Explain** the concept in plain English in the paired `.md`.
6. **Ship** — commit with the disclosure header.

---

## 🔧 Run It Yourself

```bash
# every file, always:
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _N_Name.c && ./demo

# memory-heavy files, additionally:
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo _N_Name.c && ./demo

# projects: make test / make sanitize (same targets as cpp-by-RDJ)
```

**Toolchain:** GCC 13 (`gcc --version`), C17 (`-std=c17`), zero warnings under `-Wall -Wextra -Wpedantic`, clean under AddressSanitizer and UndefinedBehaviorSanitizer.

---

## 🤝 Integrity

- This folder's **design** (curriculum, module READMEs, topic lists) was drafted with Claude; **no code exists yet**. When code is written, each file will carry the same per-file disclosure used across this repo — hand-written by RDJ, or written with Claude — stated per file, never hidden.
- No security tool here will ever target a system I don't own. The security rule is the same one the network scanner enforces in code: loopback and my own hosts only.

---

## 📈 Progress Log

| Date | Entry |
|---|---|
| 2026-11-03 | Scaffold created: 5 modules and 2 project starters fully designed (READMEs and topic lists), code not started |
