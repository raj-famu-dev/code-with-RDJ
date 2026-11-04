<div align="center">

# Project 01 — Grade Manager in C

![Status](https://img.shields.io/badge/Status-Not%20Started-F59E0B?style=for-the-badge)
![C](https://img.shields.io/badge/C-C17-A8B9CC?style=for-the-badge&logo=c&logoColor=black)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)
![Type](https://img.shields.io/badge/Type-Application-3B82F6?style=for-the-badge)

*The Java capstone, ported to C17 with structs, malloc and file persistence*

[About](#-about) •
[Goals](#-goals) •
[Definition of Done](#-definition-of-done) •
[Planned Files](#-planned-files) •
[Status Note](#-status-note)

⬅ [C Lab](../../README.md) · [Project 02](../project-02-hash-table-c/) ➡

</div>

---

## 📌 About

`project-04-grade-manager` in `java-by-RDJ` is the one application this repo's author wrote and debugged with no AI assistance. This project is its **C port** — same domain, same behavior, but implemented with the C toolkit: a `Student` struct, a dynamic array that grows with `realloc`, `fgets`+`sscanf` input handling, and persistence to a text file between runs.

It is deliberately the first project: it forces modules 01–04 together (types, structs, pointers, ownership, file I/O, Makefile) in one program small enough to hold in your head.

---

## 🎯 Goals

1. Menu-driven console app: add student, add grades, list, average, save, load, quit.
2. `struct Student` with a dynamic array of grades per student (flexible array member or `malloc`'d array).
3. Input validation with the safe `fgets` + `sscanf` pattern — no `scanf("%s")`, no `gets`.
4. Save/load to a text file with precise error reporting (`errno`, `perror`).
5. Every allocation's ownership documented and freed on every exit path.

---

## ✅ Definition of Done

- [ ] `make` builds with `-std=c17 -Wall -Wextra -Wpedantic`, zero warnings
- [ ] `make sanitize` builds and runs clean under ASan + UBSan (no leaks — LeakSanitizer clean)
- [ ] `make test` runs the test suite: `N checks, 0 failed`
- [ ] Data survives save → quit → relaunch → load
- [ ] `grade_manager.md` walkthrough exists, with a session transcript copied from a real run
- [ ] No global mutable state except the documented singletons (if any)

---

## 📂 Planned Files

| File | Purpose |
|---|---|
| `grade_manager.h` | Struct definitions, function prototypes, documentation of ownership rules |
| `grade_manager.c` | Implementation |
| `main.c` | Menu loop, argument parsing |
| `tests.c` | Test harness (`N checks, 0 failed` style) |
| `Makefile` | `make`, `make test`, `make sanitize`, `make clean` |
| `grade_manager.md` | Line-by-line walkthrough with real session transcript |

---

## 📝 Status Note

Starter only — README and definition of done written; no code. Depends on modules 01–04. Authorship will be disclosed per file when written.

---

<div align="center">

<sub>Built and owned by [Raj Patel (RDJ)](https://github.com/raj-famu-dev) — Computer Science @ **Florida A&M University** · Tallahassee, Florida · [Instagram @rdj_369](https://instagram.com/rdj_369)</sub>

[⬅ c-by-RDJ](../../README.md) · [Repository home](../../../README.md)

</div>
