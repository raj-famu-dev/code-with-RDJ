# `uninitialized_read.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Reading a variable or heap block before giving it a value gives an indeterminate result: whatever bytes happened to be there. The program may behave differently on each run, and branching on that value is undefined behaviour. This is the one bug class in this lab that **AddressSanitizer and UndefinedBehaviorSanitizer do not report**: the memory is valid and owned, it just was never initialised.

## Full Line-by-Line Breakdown

### The buggy program (`bugs/uninitialized_read.cpp`)
`make_buffer()` returns `new int[4]`. Plain `new` of an `int` array does *not* zero the memory (default-initialisation), so `values[2]` is indeterminate. The program then branches on `values[2] > 0`. Which branch runs depends on leftover bytes, so the printed line is not guaranteed to be the same everywhere. (On this machine ASan fills fresh heap memory with a recognisable byte pattern, which makes the result stable here, but that is a debugging aid of the tool, not something the language promises.)

### What the sanitizer reports (real output)
Built with `g++ -std=c++20 -g -fsanitize=address,undefined`, run as `./uninitialized_read --trigger`; exit code **0**. Directory names, process ids and addresses are normalised; the rest is the sanitizer's own text (first 6 lines of the report):

```text
(nothing was printed to stderr)
```

What the tools say, from `RESULTS.md`. Valgrind memcheck (plain `-g -O0` build without sanitizers; exit code 9 because `--error-exitcode=9` is set):

```text
==PID== Conditional jump or move depends on uninitialised value(s)
==PID==    at 0xADDR: main (uninitialized_read.cpp:20)
==PID==
```

AddressSanitizer + UBSan: no report at all (exit code 0), shown in the first block above. Valgrind's memcheck tracks whether each bit was initialised and reports `Conditional jump or move depends on uninitialised value(s)` at the branch. Clang's MemorySanitizer (`-fsanitize=memory`) is designed for this bug class, but the msan runtime library is not installed on this machine, so it was **not run** here; `make lab` records that fact instead of claiming a result.

### The fix (`bugs/fixed/uninitialized_read.cpp`)
Value-initialise: `std::vector<int>(4)` gives four zeros, `new int[4]()` also zero-fills, and for a local write `int x{};`. The fixed program does this and always takes the same branch.

Real output of the fixed program under the same sanitizer flags (exit code **0**, nothing on stderr):

```text
values[2] is zero (defined, always the same): zero or negative branch taken
local = 0
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `new int[4]` is zero-filled; a local must be definitely assigned before use or it does not compile | `new int[4]` and `int x;` leave indeterminate contents with no compile error |
| Fields default to 0/null/false | Members of a class without an initialiser are indeterminate |

## Key Rules / Gotchas Recap
- Initialise at declaration: `int x{};`, `std::vector<int>(n)`, `new T[n]()`.
- ASan and UBSan do not detect uninitialised reads; use MSan (clang) or Valgrind, and compiler warnings as a first filter.
- A passing run proves nothing: indeterminate values can happen to look fine.

## Why This Structure Exists
Uninitialised memory leaks data (stale secrets can show up in output) and makes behaviour unpredictable, so security-minded code initialises everything and uses a second tool for this class.
