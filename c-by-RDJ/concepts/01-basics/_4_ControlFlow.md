# `_4_ControlFlow.c`

## Concept
Branching in C: `if`/`else` chains and `switch`. The C twist: conditions are plain integers (`0` false, anything else true), and `switch` cases are *labels* you can fall through — the source of both a classic idiom and a classic bug.

## The Code

```c
#include <stdio.h>

int main(void) {
    int score = 72;

    if (score >= 90) {
        printf("grade A\n");
    } else if (score >= 60) {
        printf("grade: pass (%d)\n", score);
    } else {
        printf("grade: fail\n");
    }

    int day = 3;
    switch (day) {
    case 1:  printf("Mon\n"); break;
    case 2:  printf("Tue\n"); break;
    case 3:  printf("Wed\n"); break;
    case 6:
    case 7:  printf("weekend\n"); break;
    default: printf("unknown day\n"); break;
    }
    return 0;
}
```

## Line-by-Line Breakdown

### `if (score >= 90)`
The condition is an expression yielding `int`. `if (x)` means "if x is nonzero". `if (x == 5)` vs the accidental `if (x = 5)` (an assignment, always true) is why compilers warn about `=` in conditions.

### `else if` / `else`
Exactly one branch runs. Brace every branch — C has no `else` without them ambiguity, but omitting braces on multi-statement branches is a maintenance bug.

### `switch (day)`
Only works on integer types (`int`, `char`, `enum`) — **no strings, no ranges** (Java added both much later; modern C still hasn't). Each `case` is a compile-time constant *label*, and execution jumps to the matching one.

### `break`
Ends the switch. Without it, control **falls through** to the next case.

### The intentional fall-through: `case 6:` → `case 7:`
Cases 6 and 7 share one body: hitting label 6 "falls into" the weekend print. Grouping cases like this is idiomatic and expected.

### `default`
Runs when nothing matches — put it last and always include it for unhandled values.

## Traps
- **Missing `break`** is the classic C bug: `case 1` without `break` executes everything below it. GCC has `-Wimplicit-fallthrough` to catch accidents while allowing intentional ones (annotate with a comment).
- `switch` on a `char` works; on a `char*` (string) does not compile.
- Duplicate case values are a compile error.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _4_ControlFlow.c && ./demo
```

## Why This Structure Exists
`switch` compiles to a jump table — one indexed jump instead of a chain of comparisons. That speed is why C kept labels-and-fall-through even when safer designs came along.
