# `_4_MemoryBugsAndSanitizers.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Memory bugs are mistakes about who owns a piece of memory and how long it is valid: reading it after it was freed, writing past its end, never freeing it, freeing it twice, or reading it before it was ever set. In C++ none of these is stopped by the language; they are undefined behaviour, which may crash, corrupt data or appear to work. Sanitizers are compiler options that add run-time checks, so the bug is reported with a stack trace the moment it happens.

This lesson contains toy versions of each bug inside its own file. They are OFF by default and run only when you pass a flag such as `--bug=use-after-free`; nothing here attacks anything, it only breaks this one process.

## Full Line-by-Line Breakdown

### SECTION 1: SAFE REPLACEMENTS FOR EACH BUG
This is the default run. For every toy bug the program shows the modern replacement: a `unique_ptr` (single owner, so no dangling raw copy), a `vector` accessed with `at()` (throws instead of corrupting memory), a scope-bound owner that frees automatically, a moved-from `unique_ptr` that becomes null (so a second free is impossible), value-initialised memory, and widening before arithmetic.

Output from a real run:

```text
===== SECTION 1: SAFE REPLACEMENTS FOR EACH BUG =====
use-after-free fix: unique_ptr owns it, value 42
overflow fix: at(4) threw out_of_range instead of corrupting memory
leak fix: freed automatically at scope end (7)
double-free fix: after the move, a is null, b owns the int
uninit fix: vector<int>(4) starts as zeros, first = 0
signed-overflow fix: widen first -> 2147483648
```

### SECTION 2: HOW TO SEE THE BUGS
A short guide printed by the program itself: how to trigger a bug with the flag and what each sanitizer can and cannot find. ASan covers use-after-free, heap/stack/global overflow, double free and (via LeakSanitizer) leaks. UBSan covers things like signed overflow and null dereference. Neither detects uninitialised reads.

Output from a real run:

```text
===== SECTION 2: HOW TO SEE THE BUGS =====
Run with a flag, for example: ./prog --bug=use-after-free
Compile with -fsanitize=address,undefined -g to get a report instead of silent damage.
Without sanitizers these bugs are undefined behaviour: they may seem to work, crash, or corrupt data.
ASan finds: use-after-free, heap/stack/global overflow, double free, leaks (via LeakSanitizer).
UBSan finds: signed overflow, bad shifts, null deref, misaligned access. Neither finds uninit reads.
```

#### The toy bugs, one at a time (real sanitizer output)

Build once with the sanitizers, then trigger each bug by flag:

```bash
g++ -std=c++20 -g -fsanitize=address,undefined -o prog _4_MemoryBugsAndSanitizers.cpp
./prog --bug=use-after-free
```

The default run (`./prog`, no flag) executes only the safe code above and exits 0, also under the sanitizers. Each flag below runs ONE toy bug that damages only this process. Report headlines are copied from real runs; pid numbers, memory addresses and the long directory prefix were removed because they change every run, and only the headline lines are shown (the full report also lists stack traces).

**`--bug=use-after-free`**: `p` is deleted through a helper and then read. Without a sanitizer this may print 42, garbage, or crash; it is undefined behaviour.

```text
ERROR: AddressSanitizer: heap-use-after-free
SUMMARY: AddressSanitizer: heap-use-after-free _4_MemoryBugsAndSanitizers.cpp:32 in bug_use_after_free()
(exit code 1)
```

**`--bug=overflow`**: writes `buf[4]` into a 4-element heap array (one element past the end).

```text
ERROR: AddressSanitizer: heap-buffer-overflow
SUMMARY: AddressSanitizer: heap-buffer-overflow _4_MemoryBugsAndSanitizers.cpp:37 in bug_overflow(int)
(exit code 1)
```

**`--bug=leak`**: allocates with `new` and never deletes. LeakSanitizer reports at program exit, and the exit code becomes non-zero.

```text
ERROR: LeakSanitizer: detected memory leaks
SUMMARY: AddressSanitizer: 4 byte(s) leaked in 1 allocation(s).
(exit code 1)
```

**`--bug=double-free`**: `delete`s the same pointer twice.

```text
ERROR: AddressSanitizer: attempting double-free on ADDR in thread T0:
SUMMARY: AddressSanitizer: double-free ../../../../src/libsanitizer/asan/asan_new_delete.cpp:164 in operator delete(void*, unsigned long)
(exit code 1)
```

**`--bug=signed-overflow`**: computes `INT_MAX + 1`. This one is caught by UndefinedBehaviorSanitizer, which by default only prints a runtime-error line and keeps going (exit code 0, with the wrapped value printed), unlike ASan which aborts.

```text
_4_MemoryBugsAndSanitizers.cpp:61:9: runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'
(exit code 0)
```

**`--bug=uninit`**: allocates `new int[4]` WITHOUT initialising it and prints element 0. The sanitizers used here (ASan, UBSan with g++) do not detect this: AddressSanitizer fills fresh heap memory with a fixed pattern, so the program simply prints a strange number and exits with 0 (this is itself a reminder that "no sanitizer error" does not mean "no bug"):

```text
uninitialised value: -1094795586
```

To catch reads of uninitialised memory you need a different tool: Valgrind's memcheck (tried here) or MemorySanitizer in clang (not tried). Valgrind reported, for the same program built without sanitizers:

```text
Conditional jump or move depends on uninitialised value(s)
ERROR SUMMARY: 4 errors from 4 contexts (suppressed: 0 from 0)
```

(Valgrind reports the error where the garbage is first used in a decision, which here is inside the library code that prints the value; `--track-origins=yes` additionally says "Uninitialised value was created by a heap allocation".)

An unknown flag prints a usage hint and exits with code 2.

**Safe replacements** (what Section 1 of the output demonstrates): `unique_ptr` for ownership, `std::vector` with `at()` for arrays, RAII for cleanup, `std::move` to transfer a single owner, value-initialisation (`()` or `{}`) for memory, and widening types before arithmetic.

## Key Differences From Java
| Java | C++ |
|---|---|
| Use-after-free cannot happen: the GC keeps referenced objects alive | Possible: the pointer still holds the old address after `delete` |
| Out-of-bounds throws `ArrayIndexOutOfBoundsException` | Out-of-bounds `[]` is undefined behaviour: memory corruption, no exception |
| Leaks are possible only through live references (e.g. forgotten listeners) | A leak is any `new` without a matching `delete` |
| Double free impossible | `delete` twice is undefined behaviour (often a crash) |
| Variables and fields are zero/null-initialised or compiler-checked | Heap memory from `new int[4]` is uninitialised garbage |
| Integer overflow wraps silently | Signed overflow is undefined behaviour (UBSan can report it) |
| Debug tooling: heap dumps, profilers | Sanitizers (`-fsanitize=address,undefined`), Valgrind |

## Key Rules / Gotchas Recap
- The default run is safe; bugs run only with `--bug=<name>` and are meant for sanitizer builds.
- Build with `-g -fsanitize=address,undefined` during development and tests; it catches most memory bugs with a precise stack trace.
- A bug that "seems to work" without a sanitizer is still a bug: undefined behaviour has no promised outcome.
- ASan/UBSan do not find reads of uninitialised memory: use Valgrind or clang's MemorySanitizer.
- LeakSanitizer turns a leak into a non-zero exit code at program exit.
- UBSan reports and continues by default; add `-fno-sanitize-recover=undefined` to make it stop.
- Sanitizers slow the program (typically a few times) and are for testing, not production.

## Why This Structure Exists
Memory-safety bugs are the dominant class of serious vulnerabilities in native code, and the ability to reproduce one in a toy program and then read a sanitizer report is the starting point for both secure coding and legitimate vulnerability analysis in your own code or in legal training labs. Running sanitizers in continuous integration is standard practice on performance-critical systems such as inference engines.
