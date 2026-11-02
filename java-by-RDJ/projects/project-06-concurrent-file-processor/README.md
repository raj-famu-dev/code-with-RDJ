# Project 06 — Concurrent File Processor

**Status:** ⬜ Not started · **Needs:** all of `05-multithreading`, `07-file-io`, `08-lambdas-streams`

## 📌 Project Description

A tool that processes a large set of local text files (word counts, longest line, keyword search) first sequentially, then concurrently, and reports the measured difference honestly.

Use only files you generate or own. For test data, write a small generator that creates a few hundred files of random text.

## 📋 Requirements
1. Sequential baseline implementation
2. Fixed thread pool implementation with `ExecutorService`
3. `CompletableFuture` or virtual-thread implementation
4. Results merged into one report using a thread-safe structure (`ConcurrentHashMap`, or merge per-thread maps afterward)
5. Timing for each version over several runs (report the median, not the best run)
6. Graceful shutdown and a clear message when one file fails to read; one bad file does not kill the run

## Non-Functional Requirements
- No shared mutable state without a documented reason
- Pool size is configurable; test at least 1, 2, 4, 8 threads
- Explain in the `.md` why the speedup is or is not what you expected (I/O-bound vs CPU-bound)

## ✅ Definition of Done
- [ ] Source, `.md` walkthrough, requirements self-check table
- [ ] A results table with real measured numbers and your machine's core count
- [ ] A "bugs I hit" section: at least one race or deadlock you caused and fixed
