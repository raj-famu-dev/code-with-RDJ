# `_6_Searching.c`

## Concept
Linear search (works on anything, O(n)) vs binary search (needs **sorted** input, O(log n)) — hand-rolled and via the library's `bsearch`. The lesson the demo drills: *sorted input is a precondition, not a suggestion.*

## The Code

```c
#include <stdio.h>
#include <stdlib.h>

static int cmp_int(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);
}

static int linear_find(const int *a, size_t n, int target) {
    for (size_t i = 0; i < n; i++)
        if (a[i] == target) return (int)i;
    return -1;
}

static int binary_find(const int *a, size_t n, int target) {
    size_t lo = 0, hi = n;                 /* half-open range [lo, hi) */
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;   /* overflow-safe midpoint */
        if (a[mid] == target) return (int)mid;
        if (a[mid] < target) lo = mid + 1;
        else hi = mid;
    }
    return -1;
}

int main(void) {
    int sorted[10] = { 1, 3, 7, 15, 19, 26, 34, 42, 60, 88 };
    printf("binary_find(42): index %d\n", binary_find(sorted, 10, 42));
    printf("binary_find(2):  %d (absent, between elements)\n", binary_find(sorted, 10, 2));
    int unsorted[5] = { 42, 7, 19, 3, 88 };
    printf("binary_find on unsorted data finds 3: %d (WRONG — contract violated)\n",
           binary_find(unsorted, 5, 3));
    return 0;
}
```

## Line-by-Line Breakdown

### `linear_find` — the honest default
One walk, comparisons only — correct on **any** data. O(n) because the target may be anywhere (or nowhere).

### `binary_find` — halve the range
The half-open interval `[lo, hi)` is the modern convention that removes off-by-ones:
- `mid = lo + (hi - lo) / 2` — the overflow-safe midpoint (`(lo + hi) / 2` overflows on huge arrays; the famous binary-search bug that lived in Java's standard library for years).
- `a[mid] < target` → the answer is right of mid: `lo = mid + 1`; else `hi = mid`.
- Loop ends when the range is empty: not found.

Each iteration halves the search space: 10 elements → ~3.3 comparisons; a million → ~20. That log is the entire value proposition.

### `bsearch(&target, ...)` — the library version
Same algorithm, `qsort`'s interface: takes the **address of the key** (it's passed as `const void *` and compared byte-wise like an element), the array, element size, comparator. Sort with `qsort`, search with `bsearch`: one comparator serves both.

### The violated contract (the demo's point)
Binary search on **unsorted** data doesn't crash and doesn't warn — it just returns garbage (the demo's `-1` for a value that IS present). A precondition violation in C is a *wrong answer*, silently. This is why module 05's structures all document their invariants.

### Preconditions as API contracts
`binary_find`'s real contract is: *input sorted ascending, comparator consistent with the sort's*. The Java collections lab makes the same point with `Comparable`/`Comparator`; C just doesn't type-check it.

## Traps
- `(lo + hi) / 2` overflow — use `lo + (hi - lo) / 2`.
- Closed-interval `[lo, hi]` with `hi = n - 1` needs different loop bounds — mixing conventions is the classic infinite-loop/miss bug; pick half-open and stay.
- Forgetting that "sorted" includes the comparator's direction (descending data + ascending comparator = garbage).

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _6_Searching.c && ./demo
```

## Why This Structure Exists
Binary search is the payoff of sorting: pay O(n log n) once (topic 5), buy O(log n) searches forever. It's also the first "contract" algorithm every C programmer meets — the day silent wrongness becomes personal.
