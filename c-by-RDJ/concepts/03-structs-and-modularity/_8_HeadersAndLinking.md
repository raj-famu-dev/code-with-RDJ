# `_8_HeadersAndLinking.c` (with `_8_counter.h` and `_8_counter.c`)

## Concept
How multi-file C programs fit together: **headers declare, source files define, the linker stitches.** `extern` says "defined elsewhere"; `static` says "private to this file". This is the machinery `#include` and "undefined reference" errors live in.

## The Files

```c
/* _8_counter.h — the INTERFACE */
#ifndef COUNTER_H
#define COUNTER_H

extern int counter_total(void);
extern void counter_reset(void);
extern void counter_bump(void);

#endif /* COUNTER_H */
```

```c
/* _8_counter.c — the IMPLEMENTATION */
#include "_8_counter.h"

static int count = 0;        /* internal linkage: file-private */

void counter_bump(void)  { count++; }
int  counter_total(void) { return count; }
void counter_reset(void) { count = 0; }
```

```c
/* _8_HeadersAndLinking.c — the CONSUMER */
#include <stdio.h>
#include "_8_counter.h"

int main(void) {
    counter_bump();
    counter_bump();
    counter_bump();
    printf("count = %d (three bumps)\n", counter_total());
    counter_reset();
    printf("after reset = %d\n", counter_total());
    return 0;
}
```

## Piece-by-Piece Breakdown

### The header (`_8_counter.h`)
Three jobs: declare the interface, guard against double inclusion, document the contract. The `#ifndef COUNTER_H` / `#define COUNTER_H` / `#endif` **include guard** makes including the header twice (easy to do transitively) harmless — the second time, `COUNTER_H` is already defined and the preprocessor skips the body.

### `extern` declarations
A function declaration (`int counter_total(void);`) is already a promise — the definition lives elsewhere. For *variables*, `extern int x;` declares without allocating; exactly one `.c` file must define `int x;`. Zero definitions → "undefined reference" (a **linker** error); two → "multiple definition".

### `static int count = 0;` — internal linkage
At file scope, `static` means **private to this translation unit**: no other file can even name `count` (not by extern, not by include). This is C's `private` — how you hide a module's state. (`static` on a *function* means the same: invisible outside the file — perfect for helpers.)

### `#include "_8_counter.h"`
Quoted includes search the current directory first; angle brackets (`<stdio.h>`) search the system paths. `#include` is literally textual pasting — the header's declarations land in this file before compilation.

### The build: compile separately, then link
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -c _8_counter.c        # -> _8_counter.o
gcc -std=c17 -Wall -Wextra -Wpedantic -c _8_HeadersAndLinking.c  # -> _8_HeadersAndLinking.o
gcc -o demo _8_counter.o _8_HeadersAndLinking.o               # link
# or all at once:
gcc -std=c17 -Wall -Wextra -Wpedantic -o demo _8_counter.c _8_HeadersAndLinking.c
```
Each `.c` is a **translation unit** compiled in isolation (the compiler sees only what its `#include`s brought in); the **linker** then resolves every `counter_*` symbol to `_8_counter.o`. Change one file → recompile one object, relink. That incremental model is what `make` automates (Module 04, topic 7).

## Traps
- **Undefined reference**: you declared but never defined (or forgot to list the `.c`/`.o` on the link line). Linker error, not compiler error — beginners hit this daily.
- **Multiple definition**: the same symbol defined in two `.c` files — either remove one or mark helpers `static`.
- ODR's C cousin: one definition per program for non-`static` symbols; headers must therefore hold *declarations* and `static inline` functions only, never plain definitions.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _8_HeadersAndLinking.c _8_counter.c && ./demo
```

## Why This Structure Exists
The header/source/linker split is C's answer to "how do ten thousand files build together?": each compiles alone against interfaces only, and the linker resolves at the end. Every build system you'll ever use — make, CMake, an IDE — is managing exactly this pipeline.
