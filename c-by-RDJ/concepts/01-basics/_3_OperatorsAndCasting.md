# `_3_OperatorsAndCasting.c`

## Concept
Operators, integer promotion, explicit casts — and the single most important rule this module teaches: **signed integer overflow is undefined behavior in C**. Java wraps silently; C gives the compiler permission to do anything.

## The Code

```c
#include <stdio.h>

int main(void) {
    int seven = 7, two = 2;
    printf("7 / 2        = %d   (truncated, NOT 3.5)\n", seven / two);
    printf("7 %% 2        = %d   (remainder)\n", seven % two);
    printf("7.0 / 2      = %.1f (int promoted to double)\n", 7.0 / two);
    printf("(double)7/2  = %.1f (cast first, then divide)\n", (double)seven / two);

    char c = 100;
    printf("char 100 + char 100 = %d (promoted to int, no overflow)\n", c + c);

    unsigned u = 4294967295u;
    printf("UINT_MAX + 1 = %u (unsigned wraps: defined behavior)\n", u + 1);
    return 0;
}
```

## Line-by-Line Breakdown

### Integer division `7 / 2`
Both operands are `int` → the result is `int` → `3`. Java is identical. To get `3.5`, one side must be `double`.

### `(double)seven / two`
The cast binds tighter than `/`, so the division happens in `double`. Casting is explicit and unchecked — C trusts you completely.

### Integer promotion
`c + c`: two `char` values are promoted to `int` *before* the addition, so `100 + 100` cannot overflow a `char` — it's `200` as an `int`. This is the "usual arithmetic conversions" at work.

### Unsigned wraparound
`u + 1` where `u == UINT_MAX` is **defined**: unsigned arithmetic is modular (mod 2^32). This is a legitimate technique for hashing and timers.

### Signed overflow — undefined behavior (UB)
`INT_MAX + 1` in signed arithmetic has **no defined result**: the compiler may wrap, trap, or delete your code path entirely. Java's `int` wraps; C's doesn't promise anything. Compile with `-fsanitize=undefined` and the UBSan runtime reports it precisely.

## Traps
- `7 / 2 * 2 == 6`, not 7 — truncation compounds.
- `x < x + 1` is not always true for signed `x` (UB at `INT_MAX`); for unsigned it *is* true (wraparound is defined).
- Never write `i + 1 < i` overflow checks with signed types — use unsigned math.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _3_OperatorsAndCasting.c && ./demo
```

## Why This Structure Exists
C's operators map to single machine instructions, and its undefined-overflow rule exists so compilers can optimize aggressively. The cost: the programmer must reason about ranges — which is exactly what `limits.h` is for.
