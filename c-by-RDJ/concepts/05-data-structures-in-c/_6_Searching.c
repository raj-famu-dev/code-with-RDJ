// Tags: #C #DataStructures #Searching #BinarySearch | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>

/* Linear search works on ANYTHING. Binary search needs SORTED input —
   and pays back with logarithmic time. The comparator is shared with qsort. */

static int cmp_int(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);
}

/* Linear: O(n). Correct on unsorted data too. */
static int linear_find(const int *a, size_t n, int target) {
    for (size_t i = 0; i < n; i++)
        if (a[i] == target) return (int)i;
    return -1;
}

/* Binary: O(log n). PRECONDITION: a is sorted ascending. */
static int binary_find(const int *a, size_t n, int target) {
    size_t lo = 0, hi = n;               /* half-open range [lo, hi) */
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2; /* overflow-safe midpoint */
        if (a[mid] == target) return (int)mid;
        if (a[mid] < target) lo = mid + 1;
        else hi = mid;
    }
    return -1;
}

/* bsearch: the library version — same O(log n), void*-generic like qsort. */
static void *bsearch_demo(const int *a, size_t n, int target) {
    return bsearch(&target, a, n, sizeof a[0], cmp_int);   /* note: address of target */
}

int main(void) {
    int sorted[10] = { 1, 3, 7, 15, 19, 26, 34, 42, 60, 88 };

    printf("linear_find(42): index %d\n", linear_find(sorted, 10, 42));
    printf("binary_find(42): index %d\n", binary_find(sorted, 10, 42));
    printf("bsearch(42):     %s\n", bsearch_demo(sorted, 10, 42) != NULL ? "found" : "not found");

    /* Misses and edges: */
    printf("binary_find(99): %d (absent, -1)\n", binary_find(sorted, 10, 99));
    printf("binary_find(1):  %d (first element)\n", binary_find(sorted, 10, 1));
    printf("binary_find(88): %d (last element)\n", binary_find(sorted, 10, 88));
    printf("binary_find(2):  %d (absent, between elements)\n", binary_find(sorted, 10, 2));

    /* The contract, demonstrated: binary search on UNSORTED data is wrong. */
    int unsorted[5] = { 42, 7, 19, 3, 88 };
    printf("binary_find on unsorted data finds 3: %d (WRONG — contract violated)\n",
           binary_find(unsorted, 5, 3));
    printf("=> sorted input is a PRECONDITION, not a suggestion.\n");

    /* The loop count: log2(10) ~ 3.3 — binary search's whole pitch. */
    printf("log2(10) ~ 3.3 comparisons max, vs 10 for linear. At a million elements: ~20 vs ~500000.\n");
    return 0;
}
