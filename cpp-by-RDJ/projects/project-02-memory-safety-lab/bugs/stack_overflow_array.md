# `stack_overflow_array.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
This is a **stack buffer overflow**: an off-by-one loop writes one element past the end of a local array, damaging whatever lives next to it on the stack. (It is not the unrelated "stack overflow" of runaway recursion.) A local array is just a fixed number of bytes in the function's frame, and C++ does not stop an index from leaving it.

## Full Line-by-Line Breakdown

### The buggy program (`bugs/stack_overflow_array.cpp`)
`readings` is `int[4]`. The loop uses `i <= count` where `count` is 4 at run time, so the last iteration writes `readings[4]`, one past the end: the classic `<=` instead of `<`. The bound comes from `argc` so the compiler cannot warn about it. The program only touches its own stack frame.

### What the sanitizer reports (real output)
Built with `g++ -std=c++20 -g -fsanitize=address,undefined`, run as `./stack_overflow_array --trigger`; exit code **1**. Directory names, process ids and addresses are normalised; the rest is the sanitizer's own text (first 24 lines of the report):

```text
stack_overflow_array.cpp:21:19: runtime error: index 4 out of bounds for type 'int [4]'
stack_overflow_array.cpp:21:21: runtime error: store to address 0xADDR with insufficient space for an object of type 'int'
0xADDR: note: pointer points here
=================================================================
==PID==ERROR: AddressSanitizer: stack-buffer-overflow on address 0xADDR at pc 0xADDR bp 0xADDR sp 0xADDR
WRITE of size 4 at 0xADDR thread T0
    #0 0xADDR in main stack_overflow_array.cpp:21
    #1 0xADDR in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #2 0xADDR in __libc_start_main_impl ../csu/libc-start.c:360
    #3 0xADDR in _start (stack_overflow_array+0xADDR)

Address 0xADDR is located in stack of thread T0 at offset 48 in frame
    #0 0xADDR in main stack_overflow_array.cpp:12

  This frame has 1 object(s):
    [32, 48) 'readings' (line 18) <== Memory access at offset 48 overflows this variable
HINT: this may be a false positive if your program uses some custom stack unwind mechanism, swapcontext or vfork
      (longjmp and C++ exceptions *are* supported)
SUMMARY: AddressSanitizer: stack-buffer-overflow stack_overflow_array.cpp:21 in main
```

How it is caught, in two layers. UndefinedBehaviorSanitizer knows the array type is `int [4]`, so it prints `index 4 out of bounds for type 'int [4]'` and then complains about the store. AddressSanitizer reports `stack-buffer-overflow`: it surrounds local arrays with poisoned redzones, so the write to element 4 lands in a redzone. UBSan reports and continues by default, so its lines come first and ASan's report ends the run. Reading the report: bug class, `WRITE of size 4` (one `int`), then the source line of the loop.

### The fix (`bugs/fixed/stack_overflow_array.cpp`)
`std::array<int, 4>` keeps its size in the type; the loop runs to `readings.size()` with `<`. For an index that comes from elsewhere, `.at()` checks it and throws `std::out_of_range`, which the fixed program demonstrates with `readings.at(4)`.

Real output of the fixed program under the same sanitizer flags (exit code **0**, nothing on stderr):

```text
readings: 0 10 20 30
readings.at(4) threw std::out_of_range (a catchable error, not silent stack corruption)
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `int[] a = new int[4]; a[4] = 1;` throws immediately | `int a[4]; a[4] = 1;` is undefined behaviour with no check |
| `a.length` is always available | A raw array decays to a pointer and loses its length when passed to a function |

## Key Rules / Gotchas Recap
- Use `<` with `.size()`, or a range-for, never `<=` with a typed-in number.
- Prefer `std::array`/`std::vector` to raw arrays.
- Two tools see different things: UBSan knows array types, ASan knows memory.

## Why This Structure Exists
Stack buffer overflows are a classic security vulnerability; bounds-aware containers and sanitizers in the test suite are the defensive answer.
