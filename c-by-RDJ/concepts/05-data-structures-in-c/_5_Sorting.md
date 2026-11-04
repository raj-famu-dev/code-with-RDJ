# `_5_Sorting.c`

## Concept
Three sorters, one array: the library's `qsort` (callback-driven), a hand-rolled **quicksort** (Lomuto partition), and a hand-rolled **merge sort** — verified against each other, with the two classic traps (comparator overflow, pivot choice) called out.

## The Code

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int cmp_int(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);
}

static void swap(int *a, int *b) { int t = *a; *a = *b; *b = t; }

static void quicksort(int *arr, int lo, int hi) {
    if (lo >= hi) return;
    int pivot = arr[hi];
    int store = lo;
    for (int i = lo; i < hi; i++) {
        if (arr[i] < pivot) swap(&arr[i], &arr[store++]);
    }
    swap(&arr[store], &arr[hi]);
    quicksort(arr, lo, store - 1);
    quicksort(arr, store + 1, hi);
}

static void merge(int *src, int *tmp, int lo, int mid, int hi) {
    memcpy(tmp, src + lo, (size_t)(hi - lo) * sizeof(int));
    size_t i = 0, j = 0, k = (size_t)lo, n1 = (size_t)(mid - lo), n2 = (size_t)(hi - mid);
    while (i < n1 && j < n2) {
        src[k++] = (tmp[i] <= tmp[n1 + j]) ? tmp[i++] : tmp[n1 + j++];
    }
    while (i < n1) src[k++] = tmp[i++];
    while (j < n2) src[k++] = tmp[n1 + j++];
}

static void mergesort(int *arr, int *tmp, int lo, int hi) {
    if (hi - lo < 2) return;
    int mid = lo + (hi - lo) / 2;
    mergesort(arr, tmp, lo, mid);
    mergesort(arr, tmp, mid, hi);
    merge(arr, tmp, lo, mid, hi);
}

int main(void) {
    int original[10] = { 42, 7, 19, 3, 88, 15, 60, 1, 34, 26 };
    int a[10], b[10], c[10];
    memcpy(a, original, sizeof original);
    memcpy(b, original, sizeof original);
    memcpy(c, original, sizeof original);

    qsort(a, 10, sizeof a[0], cmp_int);
    quicksort(b, 0, 9);
    int tmp[10];
    mergesort(c, tmp, 0, 10);

    int agree = memcmp(a, b, sizeof a) == 0 && memcmp(a, c, sizeof a) == 0;
    printf("all three sorts identical: %s\n", agree ? "yes" : "NO!");
    return 0;
}
```

## Line-by-Line Breakdown

### `qsort(a, 10, sizeof a[0], cmp_int)`
The library sorter: takes the base pointer, count, **element size**, and a comparator (Module 03's function pointers). It swaps elements as raw `size`-byte blocks — which is why it needs the size and why the comparator gets `const void *` to cast. Fast enough for almost everything; the C++ `std::sort` lesson (templates beat the type-erased comparator) applies.

### `cmp_int`: the strict-weak-ordering contract
`negative / 0 / positive` for less/equal/greater — and it must be **consistent** (`cmp(a,a)` always 0, transitive). The `(x > y) - (x < y)` idiom is overflow-safe; `return x - y` is the classic bug (`INT_MIN - 1` wraps and flips sign). Violating the contract makes `qsort` read out of bounds — UB.

### Quicksort: the Lomuto partition
- **Pivot** = last element. **Partition:** one pass; everything smaller than the pivot moves left (`store` tracks the boundary); the pivot then lands in its **final sorted position**.
- **Recurse** on both sides; base case is 0-or-1 elements.
- Average O(n log n); **worst case O(n²)** — which happens on already-sorted input with this pivot choice (each partition peels off exactly one element). Random pivot or median-of-three fixes it; the demo states the trap.

### Merge sort: the guaranteed O(n log n)
- **Divide** in half, recurse, **merge** two sorted runs.
- The merge is the two-finger walk: compare the fronts of the two runs, take the smaller. `tmp` holds a copy of the merged range (merge sort needs O(n) extra space — the price of the guarantee).
- `tmp[i] <= tmp[...]` keeps it **stable** (equal elements keep their original order — quicksort here is not stable).

### The verification
All three sorters produce the identical array (`memcmp`) — the repo's oracle method in miniature: three independent implementations, one shared truth.

## Traps
- `x - y` comparator overflow (above).
- Quicksort on sorted input with a last-element pivot — the O(n²) trap.
- Merge sort's `tmp` must cover the full range; off-by-ones at `mid` are the classic bug (`lo + (hi - lo) / 2`, never `(lo + hi) / 2` — overflow of the sum).

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _5_Sorting.c && ./demo
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo_s _5_Sorting.c && ./demo_s
```

## Why This Structure Exists
Sorting is where C's three big ideas meet: function pointers (the comparator), arrays (the data), and recursion (the divide). One file with library + quicksort + mergesort — verified against each other — is the whole sorting story at a readable size.
