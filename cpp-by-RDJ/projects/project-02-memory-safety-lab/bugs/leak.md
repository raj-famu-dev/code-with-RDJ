# `leak.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A memory leak is a heap block that is never freed and can no longer be reached. The program keeps working, but memory use grows with every call; in a long-running service that eventually means slowdowns or a crash. LeakSanitizer finds blocks that are still allocated and unreachable when the program exits.

## Full Line-by-Line Breakdown

### The buggy program (`bugs/leak.cpp`)
`load_config()` allocates `new int[10]`, stores a value, returns it, and never calls `delete[]`. When the function returns, the local pointer disappears and the block is unreachable forever. `main` calls it three times, so three blocks of 40 bytes leak: 120 bytes in 3 objects.

### What the sanitizer reports (real output)
Built with `g++ -std=c++20 -g -fsanitize=address,undefined`, run as `./leak --trigger`; exit code **1**. Directory names, process ids and addresses are normalised; the rest is the sanitizer's own text (first 24 lines of the report):

```text
=================================================================
==PID==ERROR: LeakSanitizer: detected memory leaks

Direct leak of 120 byte(s) in 3 object(s) allocated from:
    #0 0xADDR in operator new[](unsigned long) asan_new_delete.cpp:98
    #1 0xADDR in load_config leak.cpp:11
    #2 0xADDR in main leak.cpp:23
    #3 0xADDR in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #4 0xADDR in __libc_start_main_impl ../csu/libc-start.c:360
    #5 0xADDR in _start (leak+0xADDR)

SUMMARY: AddressSanitizer: 120 byte(s) leaked in 3 allocation(s).
```

How it is caught: LeakSanitizer (part of ASan on Linux) runs at program exit. It scans the stacks, globals and registers for anything that still points into a live heap block; any block nothing points to is a leak. Reading the report: `detected memory leaks`, then `Direct leak of 120 byte(s) in 3 object(s)`: the allocations are grouped by call stack, so the three calls from `load_config` appear as one entry, and the stack shows `operator new[]` called from `load_config` (the file and line to look at).

### The fix (`bugs/fixed/leak.cpp`)
The settings live in a `std::vector<int>` local to the function. When the function returns (normally or by exception) the vector's destructor frees the block. No explicit `delete` exists, so none can be forgotten. `std::unique_ptr` does the same for single objects.

Real output of the fixed program under the same sanitizer flags (exit code **0**, nothing on stderr):

```text
total: 3 (no leak: every block was released by its owner)
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Unreachable objects are collected automatically | Unreachable heap blocks stay allocated until the process ends |
| "Leaks" in Java are objects still reachable by mistake (a forgotten static list) | C++ has those logical leaks too, plus true unreachable leaks |

## Key Rules / Gotchas Recap
- Every `new` needs exactly one matching `delete`, on every path including exceptions: let an owner do it.
- LeakSanitizer reports only at exit and only for blocks that are unreachable then.
- A leak is not memory corruption, but unbounded growth is a reliability and denial-of-service problem.

## Why This Structure Exists
Servers and tools that run for days must not grow without bound; RAII owners make leaks structurally impossible, and LeakSanitizer in tests catches the ones that slip through.
