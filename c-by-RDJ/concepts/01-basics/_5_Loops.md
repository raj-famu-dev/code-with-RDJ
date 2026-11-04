# `_5_Loops.c`

## Concept
The three C loops (`for`, `while`, `do-while`) plus `break`/`continue`. Same shapes as Java — C invented them; Java copied them.

## The Code

```c
#include <stdio.h>

int main(void) {
    int sum = 0;
    for (int i = 1; i <= 5; i++) {
        sum += i;
    }
    printf("1+2+3+4+5 = %d\n", sum);

    int n = 5, fact = 1;
    while (n > 1) {
        fact *= n--;
    }
    printf("5! = %d\n", fact);

    int countdown = 3;
    do {
        printf("countdown: %d\n", countdown--);
    } while (countdown > 0);

    for (int i = 1; i <= 6; i++) {
        if (i == 3) continue;
        if (i == 5) break;
        printf("i=%d\n", i);
    }
    return 0;
}
```

## Line-by-Line Breakdown

### `for (int i = 1; i <= 5; i++)`
Three clauses: init (scoped to the loop since C99), condition (checked *before* each pass), update (after each pass). Any clause may be empty — `for (;;)` is the idiomatic infinite loop.

### `while (n > 1)`
Condition first — the body may never run. `fact *= n--` multiplies then decrements (post-decrement returns the old value).

### `do { ... } while (cond);`
Body first, condition after — guaranteed to run at least once. Rare, but exactly right for "read input, then validate" shapes. Note the trailing `;` — forgetting it is a classic compile error.

### `continue` / `break`
`continue` jumps to the condition (for `while`) or the update clause (for `for`); `break` exits the loop entirely. Neither touches an enclosing loop — C has no labeled break like Java.

## Traps
- Infinite loops from a condition that never becomes false — C won't save you.
- `while (n-- > 0)` style tricks: make sure you can read them before you write them.
- A `;` after a loop header (`while (x);`) creates an empty-body loop.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _5_Loops.c && ./demo
```

## Why This Structure Exists
All three loops compile to the same jump + compare machine code — they exist as three spellings of one construct, for readability. Choose the one that states your intent.
