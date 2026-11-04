# `_8_MemoryOwnershipPatterns.c`

## Concept
C has no garbage collector, so code needs **ownership rules**: for every allocation, who frees it, on which path? This file shows the three idioms that answer that question in real C codebases — including the one sanctioned use of `goto`.

## The Code

```c
#include <stdio.h>
#include <stdlib.h>

int build_report(size_t rows) {
    int *data = NULL, *index = NULL, *flags = NULL;
    int rc = 1;

    data = malloc(rows * sizeof *data);
    if (!data) goto out;
    index = malloc(rows * sizeof *index);
    if (!index) goto out;
    flags = calloc(rows, sizeof *flags);
    if (!flags) goto out;

    for (size_t i = 0; i < rows; i++) { data[i] = (int)i; index[i] = (int)i; }
    rc = 0;
    printf("report built: %zu rows, data[3]=%d index[3]=%d\n", rows, data[3], index[3]);

out:
    free(flags);
    free(index);
    free(data);
    return rc;
}

int *make_copy(const int *src, size_t n) {
    int *dst = malloc(n * sizeof *dst);
    if (!dst) return NULL;
    for (size_t i = 0; i < n; i++) dst[i] = src[i];
    return dst;
}

long total(const int *data, size_t n) {
    long t = 0;
    for (size_t i = 0; i < n; i++) t += data[i];
    return t;
}

int main(void) {
    if (build_report(10) != 0) return 1;

    int original[5] = { 1, 2, 3, 4, 5 };
    int *mine = make_copy(original, 5);
    if (!mine) return 1;
    printf("borrowed sum: %ld\n", total(mine, 5));
    free(mine);
    return 0;
}
```

## Line-by-Line Breakdown

### Pattern 1: the `goto cleanup` ladder
Every pointer starts `NULL`; every allocation jumps to `out` on failure; one exit path frees **in reverse order of allocation**. The trick that makes it safe: **`free(NULL)` is a no-op**, so freeing pointers that were never assigned (or already failed) is harmless. Reverse order matters when later allocations reference earlier ones (a linked structure frees children before parents).

This is the Linux kernel's house style, and the single widely-accepted use of `goto` in modern C: one exit point instead of five near-identical cleanup blocks.

### Pattern 2: ownership transfer
`make_copy` allocates and **returns the pointer** — the caller now owns it. The contract lives in documentation (a comment or naming convention like `make_`/`dup_`). Get it wrong and you get either a leak (nobody frees) or a double-free (two think they own it).

### Pattern 3: borrowing
`total` takes `const int *` — it uses memory it did not allocate and frees nothing. `const` is the signature of a borrower. Most functions should be borrowers; only the owner touches `free`.

### The three rules that fall out
1. Every allocation has exactly **one owner**.
2. The owner frees on **every** exit path (the ladder guarantees this).
3. Borrowers never free; transfers are explicit and documented.

## Traps
- Freeing in the same order you allocated (instead of reverse) breaks when structures reference each other.
- Returning a pointer to a **stack** local — the classic dangling pointer: the scope died, the caller got garbage. (Transfer must be heap memory.)
- Two functions both believing they own one pointer: the double-free.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _8_MemoryOwnershipPatterns.c && ./demo
# verify no leaks:
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo_s _8_MemoryOwnershipPatterns.c && ./demo_s
```

## Why This Structure Exists
These three patterns are how C codebases of millions of lines (the kernel, SQLite, PostgreSQL) stay leak-free without a GC. The C++ lab's RAII automates exactly this ladder; in C, the ladder *is* the automation.
