# `double_free.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A double free releases the same heap block twice. After the first `delete` the allocator may hand the block to someone else, so the second `delete` corrupts the allocator's bookkeeping or frees another object's memory. It usually comes from two pointers that both believe they own the block.

## Full Line-by-Line Breakdown

### The buggy program (`bugs/double_free.cpp`)
`original = new int(42)` and `alias = original` are two pointers to one block. A helper `discard()` deletes through each of them in turn. Both pointers look like legitimate owners; nothing in the source says one of them must not delete.

### What the sanitizer reports (real output)
Built with `g++ -std=c++20 -g -fsanitize=address,undefined`, run as `./double_free --trigger`; exit code **1**. Directory names, process ids and addresses are normalised; the rest is the sanitizer's own text (first 24 lines of the report):

```text
=================================================================
==PID==ERROR: AddressSanitizer: attempting double-free on 0xADDR in thread T0:
    #0 0xADDR in operator delete(void*, unsigned long) asan_new_delete.cpp:164
    #1 0xADDR in discard double_free.cpp:10
    #2 0xADDR in main double_free.cpp:21
    #3 0xADDR in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #4 0xADDR in __libc_start_main_impl ../csu/libc-start.c:360
    #5 0xADDR in _start (double_free+0xADDR)

0xADDR is located 0 bytes inside of 4-byte region [0xADDR,0xADDR)
freed by thread T0 here:
    #0 0xADDR in operator delete(void*, unsigned long) asan_new_delete.cpp:164
    #1 0xADDR in discard double_free.cpp:10
    #2 0xADDR in main double_free.cpp:20
    #3 0xADDR in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #4 0xADDR in __libc_start_main_impl ../csu/libc-start.c:360
    #5 0xADDR in _start (double_free+0xADDR)

previously allocated by thread T0 here:
    #0 0xADDR in operator new(unsigned long) asan_new_delete.cpp:95
    #1 0xADDR in main double_free.cpp:18
    #2 0xADDR in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #3 0xADDR in __libc_start_main_impl ../csu/libc-start.c:360
    #4 0xADDR in _start (double_free+0xADDR)
```

How it is caught: ASan remembers which blocks are already free. The second `operator delete` call finds its block marked freed and stops with `attempting double-free`. Reading the report: unlike the others, it starts with the stack of the *second* delete (`#0 operator delete`, `#1 discard`, `#2 main` with the line numbers); ASan then prints where the block was first freed and where it was allocated.

### The fix (`bugs/fixed/double_free.cpp`)
`std::unique_ptr` models exactly one owner: copying it is a compile error (the commented-out line in the fixed file would not build), and `std::move` transfers ownership, leaving the source null (deleting a null pointer is always safe). For genuinely shared ownership use `std::shared_ptr`, where a reference count (`use_count()` 2 in the output) makes the last owner delete once.

Real output of the fixed program under the same sanitizer flags (exit code **0**, nothing on stderr):

```text
new_owner holds 42, original is null
shared value 7, owners: 2
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Two references to one object are normal; the GC frees once, when none remain | Two raw pointers to one block means two possible deleters |
| Closing a stream twice is usually harmless or an exception | Freeing twice is undefined behaviour |

## Key Rules / Gotchas Recap
- One resource, one owner: make that rule a type (`unique_ptr`).
- Aliasing raw pointers are fine for *using* a block, never for owning it.
- After handing ownership over, the old pointer must not be used or deleted.

## Why This Structure Exists
Double frees are an exploitable memory-corruption class in native code. Single-owner types turn a convention people forget into something the compiler enforces.
