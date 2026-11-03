# `use_after_free.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A use-after-free reads or writes heap memory after it has been given back to the allocator. The pointer still holds the old address, so the code looks fine, but the block now belongs to someone else (or to nobody). It is one of the most common memory-safety bug classes and a frequent root cause of real vulnerabilities, which is why AddressSanitizer is built to catch it immediately.

## Full Line-by-Line Breakdown

### The buggy program (`bugs/use_after_free.cpp`)
The program refuses to do anything without `--trigger`. With it, `new int[3]{90, 85, 77}` allocates 12 bytes, a helper `release()` calls `delete[]`, and then `scores[0]` is read through the stale pointer. The helper is deliberately a separate function: the caller's pointer is not cleared, so nothing in `main` looks wrong. Only the allocator knows the block is gone.

### What the sanitizer reports (real output)
Built with `g++ -std=c++20 -g -fsanitize=address,undefined`, run as `./use_after_free --trigger`; exit code **1**. Directory names, process ids and addresses are normalised; the rest is the sanitizer's own text (first 24 lines of the report):

```text
=================================================================
==PID==ERROR: AddressSanitizer: heap-use-after-free on address 0xADDR at pc 0xADDR bp 0xADDR sp 0xADDR
READ of size 4 at 0xADDR thread T0
    #0 0xADDR in main use_after_free.cpp:21
    #1 0xADDR in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #2 0xADDR in __libc_start_main_impl ../csu/libc-start.c:360
    #3 0xADDR in _start (use_after_free+0xADDR)

0xADDR is located 0 bytes inside of 12-byte region [0xADDR,0xADDR)
freed by thread T0 here:
    #0 0xADDR in operator delete[](void*) asan_new_delete.cpp:155
    #1 0xADDR in release use_after_free.cpp:10
    #2 0xADDR in main use_after_free.cpp:19
    #3 0xADDR in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #4 0xADDR in __libc_start_main_impl ../csu/libc-start.c:360
    #5 0xADDR in _start (use_after_free+0xADDR)

previously allocated by thread T0 here:
    #0 0xADDR in operator new[](unsigned long) asan_new_delete.cpp:98
    #1 0xADDR in main use_after_free.cpp:18
    #2 0xADDR in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #3 0xADDR in __libc_start_main_impl ../csu/libc-start.c:360
    #4 0xADDR in _start (use_after_free+0xADDR)
```

How it is caught: AddressSanitizer replaces `new`/`delete`, keeps a *shadow map* of which bytes are valid, marks freed blocks as poisoned and holds them in a quarantine instead of reusing them at once. The compiler inserts a shadow check before every memory access, so the READ of size 4 hits poisoned bytes. Reading the report: line 1 names the bug class (`heap-use-after-free`), line 2 says whether the access was a READ or WRITE and how big, the stack under it points at the offending source line, and further down ASan shows where the block was freed and where it was allocated.

### The fix (`bugs/fixed/use_after_free.cpp`)
The data lives in a `std::vector<int>` (or a `std::unique_ptr<int[]>`). The owner frees the memory only when it goes out of scope, so no pointer can outlive it as long as references are not kept past the owner's lifetime. This is RAII: tie the lifetime of the resource to a scope.

Real output of the fixed program under the same sanitizer flags (exit code **0**, nothing on stderr):

```text
score: 90 (owner: std::vector, freed automatically at end of scope)
score via unique_ptr: 90
```

## Key Differences From Java
| Java | C++ |
|---|---|
| The garbage collector only frees objects nothing references, so a stale reference cannot touch freed memory | `delete` frees at once and the old pointer is not cleared |
| The closest Java bug is using a resource after `close()` (an exception, not memory corruption) | Using freed memory is undefined behaviour: it may crash, print garbage or appear to work |

## Key Rules / Gotchas Recap
- Deleting does not null the pointer; a dangling pointer looks valid.
- Prefer owners (`std::vector`, `std::unique_ptr`) over raw `new`/`delete`.
- Never return a pointer or reference to something that dies at the end of its scope.
- "It printed the right number" proves nothing: undefined behaviour can look correct.

## Why This Structure Exists
Use-after-free is a leading cause of exploitable vulnerabilities in browsers and servers. Learning to recognise it, and to make it impossible with ownership types, is core to secure systems work.
