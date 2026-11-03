# `heap_overflow.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A heap buffer overflow writes (or reads) past the end of a `new`-allocated block. The extra bytes belong to whatever sits next to the block, so the program corrupts memory it does not own. C++ arrays and raw blocks carry no length, so nothing stops the loop.

## Full Line-by-Line Breakdown

### The buggy program (`bugs/heap_overflow.cpp`)
`name` is an 8-byte block (`new char[8]`). The loop bound `wanted` is computed at run time (12 with `--trigger`), and the loop writes `'A'` into `name[i]` for every `i < wanted`. Nothing connects the loop bound to the block size, which is the classic mistake. The bound is computed from `argc` so that the compiler cannot see the problem at compile time and so the bug is only found when the program runs under the sanitizer.

### What the sanitizer reports (real output)
Built with `g++ -std=c++20 -g -fsanitize=address,undefined`, run as `./heap_overflow --trigger`; exit code **1**. Directory names, process ids and addresses are normalised; the rest is the sanitizer's own text (first 24 lines of the report):

```text
=================================================================
==PID==ERROR: AddressSanitizer: heap-buffer-overflow on address 0xADDR at pc 0xADDR bp 0xADDR sp 0xADDR
WRITE of size 1 at 0xADDR thread T0
    #0 0xADDR in main heap_overflow.cpp:21
    #1 0xADDR in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #2 0xADDR in __libc_start_main_impl ../csu/libc-start.c:360
    #3 0xADDR in _start (heap_overflow+0xADDR)

0xADDR is located 0 bytes after 8-byte region [0xADDR,0xADDR)
allocated by thread T0 here:
    #0 0xADDR in operator new[](unsigned long) asan_new_delete.cpp:98
    #1 0xADDR in main heap_overflow.cpp:19
    #2 0xADDR in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #3 0xADDR in __libc_start_main_impl ../csu/libc-start.c:360
    #4 0xADDR in _start (heap_overflow+0xADDR)

SUMMARY: AddressSanitizer: heap-buffer-overflow heap_overflow.cpp:21 in main
```

How it is caught: ASan puts poisoned *redzones* on both sides of every heap block, so the first byte written past the end lands in a redzone and the shadow check fires. Reading the report: `heap-buffer-overflow`, a `WRITE of size 1` (one `char`), the source line, and the line `0 bytes after 8-byte region` which says the very first byte past the end was hit.

### The fix (`bugs/fixed/heap_overflow.cpp`)
`std::string` knows its length and grows when characters are appended, so there is no fixed block to overrun. When a hard size limit is real, check it, or use `.at(i)`, which throws `std::out_of_range` (a catchable error) instead of corrupting memory; the fixed program demonstrates that.

Real output of the fixed program under the same sanitizer flags (exit code **0**, nothing on stderr):

```text
string of 12 characters, first byte: A
name.at(12) threw std::out_of_range (a catchable error, not silent memory damage)
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Every array access is bounds-checked and throws `ArrayIndexOutOfBoundsException` | `p[i]` on a raw block or `operator[]` is unchecked; out of range is undefined behaviour |
| `StringBuilder` grows automatically | `std::string` grows too, but a raw `char*` buffer does not |

## Key Rules / Gotchas Recap
- A raw pointer has no size; the programmer must carry it.
- Prefer `std::string`, `std::vector`, `std::array` and `.at()` when an index comes from outside.
- Loop to the container's `.size()`, not to a number you typed earlier.
- Compile-time warnings cannot see most run-time bounds problems; sanitizers can.

## Why This Structure Exists
Buffer overflows are the textbook memory-safety vulnerability. Defensive C++ means using types that know their size, and running tests under ASan so mistakes surface in development.
