# `_3_ArraysAndPointers.c`

## Concept
Arrays and pointers are not the same thing — but an array **decays** into a pointer to its first element in almost every context. That decay loses the array's length, which is why every C function that takes an array also takes a size.

## The Code

```c
#include <stdio.h>

int sum_ints(const int *data, size_t n) {
    int total = 0;
    for (size_t i = 0; i < n; i++) {
        total += data[i];
    }
    return total;
}

void grid_demo(void) {
    int grid[2][3] = { { 1, 2, 3 }, { 4, 5, 6 } };
    printf("grid[1][2] = %d, sizeof grid = %zu\n", grid[1][2], sizeof grid);
}

void jagged_demo(void) {
    int row0[] = { 1, 2 };
    int row1[] = { 3, 4, 5 };
    int *m[2] = { row0, row1 };
    printf("jagged m[1][2] = %d (rows of different lengths)\n", m[1][2]);
}

int main(void) {
    int a[5] = { 1, 2, 3, 4, 5 };

    int *p = a;
    printf("*p = %d, but sizeof a = %zu (only the ARRAY keeps its size)\n", *p, sizeof a);
    printf("sizeof p = %zu (a pointer is just 8 bytes)\n", sizeof p);

    printf("sum = %d\n", sum_ints(a, sizeof a / sizeof a[0]));

    grid_demo();
    jagged_demo();
    return 0;
}
```

## Line-by-Line Breakdown

### Decay: `int *p = a;`
In this expression, `a` (the array) becomes `&a[0]` (a pointer). It's an implicit conversion that happens almost everywhere — assignments, function calls, arithmetic.

### `sizeof a` — the exception
`sizeof` is one of the few contexts where decay does **not** happen: `sizeof a` is the whole array's bytes (20), while `sizeof p` is the pointer's (8). This asymmetry is exactly why the `sizeof a / sizeof a[0]` length idiom works — but only in the scope where the array itself is visible.

### `sum_ints(a, 5)`
Inside the function, `data` is a pointer — it cannot know the array's length. So the length is a separate parameter. **This contract (pointer + size) is the C idiom**, and forgetting the size half is how buffer overruns are born.

### `int grid[2][3]` — real 2-D
One contiguous block of 6 ints. `grid[1]` is an array of 3 ints (which decays to a pointer when used). Row-major, exactly like Java's `int[2][3]` in memory — but with no length metadata.

### `int *m[2]` — jagged
An array of two pointers; each row is an independent array. Rows can have different lengths. `m[1][2]` follows a pointer, then indexes. This is what `char *argv[]` is (Module 04).

### `const int *data`
"Pointer to const int" — the function promises not to modify the elements. The canonical way to accept read-only arrays.

## Traps
- `sizeof a / sizeof a[0]` inside a function that received `a` as a parameter gives the *pointer's* size over element size — garbage (usually `8/4 = 2`).
- `int *p[3]` vs `int (*p)[3]`: the first is an array of pointers; the second is a pointer to an array of 3. Parentheses matter.
- Assigning `grid` (type `int (*)[3]`) to an `int *` is a type error — 2-D decay is one level deep only.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _3_ArraysAndPointers.c && ./demo
```

## Why This Structure Exists
Decay lets one function body work on any array regardless of length — the length travels separately. It's minimal and fast, and it puts the burden of remembering the size exactly where C puts every burden: on you.
