# `_6_PreprocessorAndMacros.c`

## Concept
The preprocessor is a **text-substitution pass** that runs before the compiler: `#include` pastes files, `#define` replaces names with text, `#if` deletes code at build time. Macros are powerful precisely because they ignore C's rules — which is also every macro bug.

## The Code

```c
#include <stdio.h>

#define MAX_NAME 32
#define MAX_BROKEN(a, b) a > b ? a : b
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define LOG_ERROR(msg) do { fprintf(stderr, "[error] %s:%d %s\n", __FILE__, __LINE__, msg); } while (0)

#define DEBUG_BUILD 1
#define STRINGIFY(x) #x
#define CONCAT(a, b) a##b

int main(void) {
    printf("__FILE__ = %s, __LINE__ = %d\n", __FILE__, __LINE__);
    int x = 10, y = 5;
    printf("MAX(x, y) = %d\n", MAX(x, y));
    printf("MAX(x + 1, y) = %d\n", MAX(x + 1, y));
    LOG_ERROR("a demo error with file and line");
#if DEBUG_BUILD
    printf("debug build: DEBUG_BUILD was 1 at preprocess time\n");
#else
    printf("release build\n");
#endif
    printf("STRINGIFY(42) = %s\n", STRINGIFY(42));
    printf("CONCAT(hello, world) = %d\n", CONCAT(hello, world));
    return 0;
}
```

## Piece-by-Piece Breakdown

### `#define MAX_NAME 32`
Object-like macro: plain text replacement, everywhere, forever (until `#undef`). No type, no scope, no debuggability — prefer `static const int` for constants in real code.

### The precedence bug: `MAX_BROKEN`
`MAX_BROKEN(x + 1, y)` expands to `x + 1 > y ? x + 1 : y` — fine here, but `MAX_BROKEN(a, b) * 2` becomes `a > b ? a : b * 2`. **Macro arguments must be parenthesized, and the whole body too.** The fixed `MAX` is immune.

### The multi-statement bug and `do/while(0)`
A macro of two statements breaks under `if`:
```c
#define BAD do_this(); do_that()
if (cond) BAD;        /* do_that() runs UNCONDITIONALLY */
```
`do { ... } while (0)` wraps the body into exactly one statement that expects a semicolon — the standard macro-body idiom.

### Predefined macros
`__FILE__`, `__LINE__`, `__DATE__`, `__TIME__`, `__STDC_VERSION__` — the compiler's facts about the current compilation. `LOG_ERROR` shows the payoff: log location without runtime cost.

### `#if` / `#else` — build-time switches
The preprocessor *deletes* the untaken branch — dead code that costs nothing in the binary. That's how debug logging, platform code (`#ifdef _WIN32`), and include guards all work.

### `#x` and `##`
`STRINGIFY(42)` → the literal `"42"`; `CONCAT(hello, world)` → the single token `helloworld` (the demo declares it as a variable). These build the generation machinery of real headers.

## Traps
- Macros have **no type checking** and evaluate arguments on every use: `MAX(i++, j++)` increments twice per comparison.
- Side effects + short-circuiting macros = UB-shaped surprises.
- A macro's missing parentheses compiles fine and fails at runtime — the worst bug class in C. Prefer `static inline` functions whenever a macro isn't needed for types or tokens.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _6_PreprocessorAndMacros.c && ./demo
gcc -E -P _6_PreprocessorAndMacros.c | head -20   # SEE the text substitution
```

## Why This Structure Exists
The preprocessor predates the C compiler — it was the original module system. Everything from include guards (topic 8) to `assert` to feature-test macros is this one text pass; understanding it is understanding what `#include` *actually does*.
