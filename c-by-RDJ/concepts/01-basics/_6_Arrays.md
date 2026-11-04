# `_6_Arrays.c`

## Concept
Arrays in C: fixed-size, contiguous, and **completely unchecked**. There is no `.length` field, no exception on a bad index — the most important difference from Java arrays.

## The Code

```c
#include <stdio.h>

int main(void) {
    int scores[5] = { 90, 85, 77, 95, 60 };

    size_t n = sizeof scores / sizeof scores[0];
    printf("length: %zu\n", n);

    int sum = 0;
    for (size_t i = 0; i < n; i++) {
        sum += scores[i];
    }
    printf("average: %.1f\n", (double)sum / (double)n);

    int sparse[5] = { 1, 2 };
    int by_index[5] = { [2] = 30, [4] = 50 };
    printf("sparse: %d %d %d %d %d\n", sparse[0], sparse[1], sparse[2], sparse[3], sparse[4]);
    printf("by_index: %d %d %d %d %d\n", by_index[0], by_index[1], by_index[2], by_index[3], by_index[4]);

    int grid[2][3] = { { 1, 2, 3 }, { 4, 5, 6 } };
    printf("grid[1][2] = %d\n", grid[1][2]);
    printf("sizeof grid = %zu (2*3 ints)\n", sizeof grid);

    printf("scores[4] is the last valid index; scores[5] would be undefined behavior.\n");
    return 0;
}
```

## Line-by-Line Breakdown

### `int scores[5]`
Five `int`s side by side in memory — `20` contiguous bytes. The size must be a compile-time constant (or a constant expression). Java's `new int[5]` allocates on the heap with a length; C's array is just a region of the stack.

### `sizeof scores / sizeof scores[0]`
The length idiom: whole array's bytes ÷ one element's bytes. Works only on *arrays* — once an array decays to a pointer (Module 02), `sizeof` gives the pointer's size, not the array's. This is the #1 source of bugs the idiom causes.

### Partial + designated initializers
`{ 1, 2 }` zeroes the rest. `{ [2] = 30 }` (C99) sets index 2 and zeroes everything else — great for lookup tables.

### `int grid[2][3]`
An array of two arrays of three ints — one contiguous block, 24 bytes. `grid[1][2]` walks to `1*3 + 2 =` the 6th int.

### Out of bounds = undefined behavior
`scores[5]` reads whatever bytes follow the array. It might "work", might crash, might silently corrupt another variable. The compiler inserts **no check**. ASan catches it at runtime (`-fsanitize=address`).

## Traps
- Passing an array to a function "loses" its length (it decays to a pointer) — always pass the length alongside.
- `int a[n]` with a runtime `n` is a VLA (variable-length array) — optional in C11+, avoid it.
- `sizeof a / sizeof a[0]` in a function that received `a` as a parameter is a silent bug.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _6_Arrays.c && ./demo
```

## Why This Structure Exists
A C array is the hardware's idea of a collection: a base address plus an index times an element size. No metadata, because metadata costs the machine something — and because pointers (next module) make the same region usable in a hundred other ways.
