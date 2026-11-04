// Tags: #C #DataStructures #Sorting #Qsort #Quicksort | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ---------- 1. qsort: the standard library's sorter ---------- */
/* The contract (Module 03 topic 7): negative / 0 / positive for less/equal/greater. */
static int cmp_int(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);          /* overflow-safe; NEVER 'x - y' */
}

/* ---------- 2. Hand-rolled quicksort: Lomuto partition ---------- */
static void swap(int *a, int *b) { int t = *a; *a = *b; *b = t; }

static void quicksort(int *arr, int lo, int hi) {
    if (lo >= hi) return;                      /* 0 or 1 elements: sorted */
    int pivot = arr[hi];                       /* last element as pivot */
    int store = lo;
    for (int i = lo; i < hi; i++) {
        if (arr[i] < pivot) swap(&arr[i], &arr[store++]);   /* smalls go left */
    }
    swap(&arr[store], &arr[hi]);               /* pivot into its final slot */
    quicksort(arr, lo, store - 1);              /* recurse both sides */
    quicksort(arr, store + 1, hi);
}

/* ---------- 3. Hand-rolled merge sort: the O(n log n) guarantee ---------- */
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
    if (hi - lo < 2) return;                    /* 0 or 1 elements */
    int mid = lo + (hi - lo) / 2;
    mergesort(arr, tmp, lo, mid);
    mergesort(arr, tmp, mid, hi);
    merge(arr, tmp, lo, mid, hi);
}

static void show(const char *label, const int *a, int n) {
    printf("%s:", label);
    for (int i = 0; i < n; i++) printf(" %d", a[i]);
    printf("\n");
}

int main(void) {
    int original[10] = { 42, 7, 19, 3, 88, 15, 60, 1, 34, 26 };
    int a[10], b[10], c[10];
    memcpy(a, original, sizeof original);
    memcpy(b, original, sizeof original);
    memcpy(c, original, sizeof original);

    qsort(a, 10, sizeof a[0], cmp_int);
    show("qsort     ", a, 10);

    quicksort(b, 0, 9);
    show("quicksort ", b, 10);

    int tmp[10];
    mergesort(c, tmp, 0, 10);
    show("mergesort ", c, 10);

    /* VERIFY: all three agree with each other. */
    int agree = memcmp(a, b, sizeof a) == 0 && memcmp(a, c, sizeof a) == 0;
    printf("all three sorts identical: %s\n", agree ? "yes" : "NO!");

    /* THE COMPARATOR RULE: strict weak ordering. 'x - y' looks clever and
       overflows on extremes (INT_MIN - 1); '(x>y)-(x<y)' cannot. */
    printf("comparator: (x>y)-(x<y) is overflow-safe; 'x-y' is the classic bug.\n");

    /* The pivot choice: LAST element is simple but degrades to O(n^2) on
       sorted input. Random pivot is the practical fix; introsort is what
       real libraries do. */
    printf("pivot: last-element is teaching-simple; sorted input makes it O(n^2).\n");
    return 0;
}
