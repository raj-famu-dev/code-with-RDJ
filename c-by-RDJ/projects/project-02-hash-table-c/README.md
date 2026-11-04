<div align="center">

# Project 02 — Hash Table in C

![Status](https://img.shields.io/badge/Status-Not%20Started-F59E0B?style=for-the-badge)
![C](https://img.shields.io/badge/C-C17-A8B9CC?style=for-the-badge&logo=c&logoColor=black)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)
![Type](https://img.shields.io/badge/Type-Library%20+%20Tests-3B82F6?style=for-the-badge)

*A production-shaped hash table: chaining, resize, iterators, oracle-checked*

[About](#-about) •
[Goals](#-goals) •
[Definition of Done](#-definition-of-done) •
[Planned Files](#-planned-files) •
[Status Note](#-status-note)

⬅ [Project 01](../project-01-grade-manager-c/) · [C Lab](../../README.md)

</div>

---

## 📌 About

Module 05's `_4_HashTable.c` teaches the structure; this project **hardens it into a real deliverable** — the same arc as `cpp-by-RDJ/project-01` (from-scratch structures, oracle-checked) and the repo's running theme: prove it, don't claim it.

A string-keyed hash table with separate chaining, automatic resizing, clean ownership rules, and a test suite that runs seeded random operations against an independent reference (a sorted-array oracle) — the method used across this whole repo, in C.

---

## 🎯 Goals

1. `hash_table_new/free`, `insert`, `get`, `remove`, `size`, `for_each` iteration.
2. String hashing with FNV-1a; chaining buckets; resize at load factor 0.75 with rehash.
3. Ownership documented: table owns keys (copied on insert) and its buckets; caller owns values (or the table copies them — pick one, document it).
4. Oracle testing: thousands of seeded random ops (`mt`-style RNG or `rand_r`) checked against a reference structure.
5. Measured results: bucket chain lengths, rehash counts, copies — printed from real runs.

---

## ✅ Definition of Done

- [ ] `make` builds with `-std=c17 -Wall -Wextra -Wpedantic`, zero warnings
- [ ] `make test`: `N checks, 0 failed`, including a full oracle run and edge cases (NULL args, missing keys, duplicate keys)
- [ ] `make sanitize` clean under ASan + UBSan + LeakSanitizer (zero leaks)
- [ ] Seeded runs reproducible; results in `hash_table.md` copied from real runs
- [ ] Every function's ownership documented in `hash_table.h`
- [ ] Measured stats (chain length distribution, rehashes) included in the walkthrough

---

## 📂 Planned Files

| File | Purpose |
|---|---|
| `hash_table.h` | Public API + ownership documentation |
| `hash_table.c` | Implementation |
| `tests.c` | Test harness + seeded oracle comparison |
| `Makefile` | `make`, `make test`, `make sanitize`, `make clean` |
| `hash_table.md` | Design walkthrough with measured results |

---

## 📝 Status Note

Starter only — README and definition of done written; no code. Depends on module 05. Authorship will be disclosed per file when written.

---

<div align="center">

<sub>Built and owned by [Raj Patel (RDJ)](https://github.com/raj-famu-dev) — Computer Science @ **Florida A&M University** · Tallahassee, Florida · [Instagram @rdj_369](https://instagram.com/rdj_369)</sub>

[⬅ c-by-RDJ](../../README.md) · [Repository home](../../../README.md)

</div>
