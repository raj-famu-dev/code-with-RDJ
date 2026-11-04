# `_2_PointerArithmetic.c`

## Concept
`p + 1` moves the pointer by **one element**, not one byte. This single rule makes arrays and pointers interchangeable in practice, and it's the foundation of every loop over a buffer in C.

## The Code

```c
#include <stdio.h>

int main(void) {
    int a[5] = { 10, 20, 30, 40, 50 };

    int *p = a;
    printf("*p = %d\n", *p);
    printf("*(p+1) = %d\n", *(p + 1));
    printf("*(p+3) = %d\n", *(p + 3));

    printf("a[2] = %d and *(a+2) = %d — the same thing\n", a[2], *(a + 2));
    printf("2[a] = %d — commutative addition, legal and unidiomatic\n", 2[a]);

    int *start = a;
    int *end = &a[4];
    printf("distance a..a[4] = %td elements (ptrdiff_t)\n", end - start);

    int *one_past = a + 5;
    printf("a+5 = %p (one-past-the-end: comparable, NOT dereferenceable)\n", (void *)one_past);
    return 0;
}
```

## Line-by-Line Breakdown

### `int *p = a;`
The array name **decays** to a pointer to its first element (`&a[0]`). Not a copy of the array — the same memory, viewed as a pointer.

### `*(p + 1) == 20`
`p + 1` advances by `sizeof(int)` bytes — 4 — so it lands on `a[1]`. The pointer's type drives the step size: `char *` steps 1 byte, `double *` steps 8.

### `a[i]` is `*(a + i)`
The subscript operator is *defined* as pointer arithmetic plus a dereference. That's why `2[a]` compiles (addition commutes) — a curiosity that proves the rule.

### `end - start` → `ptrdiff_t`
Pointer subtraction yields the **element count** between two pointers into the same array. `%td` prints it. (Byte count would be `4 * that` — the demo computes both.)

### `a + 5` — one past the end
Computing a pointer one past the array's last element is legal — it's the natural loop bound. **Dereferencing it is undefined behavior.** This exact rule is why `for (p = a; p < a + n; p++)` is correct and `<=` is a bug.

### Comparisons
`<`, `>`, `==` between pointers are defined for pointers into the same array (or one past its end). Comparing unrelated pointers is unspecified.

## Traps
- Arithmetic on a pointer NOT into an array is undefined (except the null case).
- `void *` has no element size — you cannot do arithmetic on it without casting.
- `p - 1` before the first element is UB, just like `a + 5` dereferenced.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _2_PointerArithmetic.c && ./demo
```

## Why This Structure Exists
Element-sized steps mean the compiler — not you — tracks the byte width. One uniform rule powers array iteration, `memcpy`-style walking, and every string function in `<string.h>`.
