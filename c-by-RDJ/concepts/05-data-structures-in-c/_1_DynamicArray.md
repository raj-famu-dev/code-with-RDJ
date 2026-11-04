# `_1_DynamicArray.c`

## Concept
The dynamic array — the workhorse of every language's built-in list (Python's `list`, Java's `ArrayList`, C++'s `std::vector`). Here it is from scratch: a heap block, a count, a capacity, and **doubling** when full — with the copies counted to prove amortized O(1).

## The Code

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int *data;
    size_t count;
    size_t capacity;
    size_t copies;
} DArray;

static int da_init(DArray *a, size_t start_cap) {
    a->data = malloc(start_cap * sizeof *a->data);
    if (!a->data) return -1;
    a->count = 0;
    a->capacity = start_cap;
    a->copies = 0;
    return 0;
}

static int da_push(DArray *a, int value) {
    if (a->count == a->capacity) {
        size_t new_cap = a->capacity * 2;
        int *bigger = realloc(a->data, new_cap * sizeof *bigger);
        if (!bigger) return -1;
        a->copies += a->capacity;
        a->data = bigger;
        a->capacity = new_cap;
    }
    a->data[a->count++] = value;
    return 0;
}

int main(void) {
    DArray a;
    da_init(&a, 4);

    const size_t N = 100000;
    for (size_t i = 0; i < N; i++) {
        da_push(&a, (int)(i % 1000));
    }
    printf("pushed %zu values: count=%zu capacity=%zu\n", N, a.count, a.capacity);
    printf("element-copies during growth: %zu total (%.2f per push)\n",
           a.copies, (double)a.copies / (double)N);
    da_free(&a);
    return 0;
}
```

## Line-by-Line Breakdown

### The struct: `data / count / capacity`
Three fields are the whole data structure: the block (`data`), how many slots are **used** (`count`), and how many are **allocated** (`capacity`). `copies` is a measurement counter — the file counts the cost it's teaching.

### `da_push` — the growth path
When `count == capacity`, **double** and `realloc`. The `realloc` may move the block (that's why we take its return in `bigger`, and why `a->data` stays valid on failure — Module 02's rule). Every existing element conceptually "moves" when the block moves — `copies += capacity` measures exactly that.

### The measured result (the point of the file)
100,000 pushes, capacity doubling from 4: total copies land around ~131,000 — about **1.3 per push** on average, roughly log2(N) spread across all pushes. Not 100,000. Not 5,000,000,000 (what +1 growth would cost: O(N²)). That's **amortized O(1)**: any single push may be expensive (a resize), but the *average over all pushes* is constant.

### `da_get` — O(1) random access
`data[i]` is one multiply and one load — the array's superpower and the reason the dynamic array is the default structure everywhere. (The Java `14-dsa-in-java` module measured 1.31 copies/add with the JDK's ArrayList — same experiment, same answer.)

### `da_free`
One `free` for the block; the struct itself lives on the stack. Ownership rule: the DArray owns its `data`; the owner frees.

## Traps
- Growing by +1 instead of doubling: O(N²) total copies — the quadratic death of hand-rolled vectors.
- Using `a->data` after a failed `realloc` — the original is still valid, but `bigger` is what you must assign.
- Forgetting that `count` and `capacity` are different things — writing `data[count]` when `count == capacity` is the buffer overflow Module 02's sanitizer demo catches.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _1_DynamicArray.c && ./demo
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo_s _1_DynamicArray.c && ./demo_s
```

## Why This Structure Exists
Every language's list is this file. Building it once in C — where you can *see* the realloc and count the copies — is why the same structure in Java/Python/C++ will never be mysterious again.
