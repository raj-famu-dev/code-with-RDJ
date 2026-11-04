# `_7_FunctionPointers.c`

## Concept
Functions live in memory at addresses — and a variable can hold that address. Function pointers are C's callbacks, dispatch tables, and the entire extensibility mechanism of the standard library (`qsort`'s comparator is one).

## The Code

```c
#include <stdio.h>
#include <stdlib.h>

int add(int a, int b) { return a + b; }
int mul(int a, int b) { return a * b; }

int apply(int (*op)(int, int), int x, int y) {
    return op(x, y);
}

int neg(int a, int b) { return a - b; }
int divi(int a, int b) { return b != 0 ? a / b : 0; }

int cmp_int_asc(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);
}
int cmp_int_desc(const void *a, const void *b) {
    return cmp_int_asc(b, a);
}

int main(void) {
    int (*op)(int, int) = add;
    printf("op(3, 4) = %d\n", op(3, 4));
    op = mul;
    printf("op(3, 4) = %d (same call site, different function)\n", op(3, 4));

    printf("apply(add, 3, 4) = %d\n", apply(add, 3, 4));

    int (*ops[4])(int, int) = { add, mul, neg, divi };
    const char *names[4] = { "add", "mul", "sub", "div" };
    for (int i = 0; i < 4; i++)
        printf("%s(10, 2) = %d\n", names[i], ops[i](10, 2));

    int data[6] = { 42, 7, 19, 3, 88, 15 };
    qsort(data, 6, sizeof data[0], cmp_int_asc);
    return 0;
}
```

## Line-by-Line Breakdown

### `int (*op)(int, int)`
Read it as: "`op` is a **pointer to** a function taking `(int, int)` and returning `int`." The parentheses around `(*op)` are mandatory: `int *op(int, int)` would declare a *function* returning `int *`. This is the trickiest declaration syntax in C — `typedef` (topic 2) tames it.

### `op = add;`
The function's name decays to its address, like an array's (no `&` needed; `&add` also works). `op(3, 4)` calls through the pointer — same syntax as a normal call.

### `apply(int (*op)(int, int), ...)`
**The callback**: behavior passed as data. This is how `qsort`, `atexit`, signal handlers, and every GUI/event API in C work. It's Java's `interface` with one method — minus the type safety (any matching signature fits).

### The dispatch table `int (*ops[4])(int, int)`
An array of function pointers, walked with data (`names`). This replaces a `switch` with a table lookup — the standard technique for command handlers, state machines, and jump tables (the `switch` in topic 4 compiles into something like this).

### `cmp_int_asc` — the `qsort` comparator contract
`qsort` calls your function with two `const void *` pointers to the elements. Your job: cast them, and return **negative / zero / positive** for less / equal / greater. The `(x > y) - (x < y)` idiom avoids overflow (never `return x - y` — it overflows on extremes).

### `cmp_int_desc` reuses `cmp_int_asc`
Swapping the arguments reverses the order — comparators compose.

## Traps
- Calling through a NULL or garbage function pointer is UB (usually an instant crash — check before calling, like any pointer).
- The comparator must be **strict weak ordering**: `cmp(a, a)` must be 0, never "greater". Violations make `qsort` read out of bounds.
- Type-mismatched function pointers (wrong signature) compile with a warning and are UB when called.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _7_FunctionPointers.c && ./demo
```

## Why This Structure Exists
Without classes or interfaces, function pointers are C's only way to hand behavior across a boundary. Every C API that "takes a hook" (`qsort`, `pthread_create`'s start routine, signal handlers) is this mechanism — and Module 05's sorting topic builds directly on it.
