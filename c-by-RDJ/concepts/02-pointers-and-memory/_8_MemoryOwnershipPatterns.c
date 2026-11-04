// Tags: #C #MemoryManagement #Ownership #GotoCleanup | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>

/* THE CLEANUP PROBLEM: three allocations, several failure exits.
   Without a pattern, each exit must remember each free — and misses are leaks. */

/* PATTERN 1: the goto cleanup ladder (the Linux-kernel idiom).
   goto is frowned upon EXCEPT here: one exit point, frees in reverse order. */
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
    rc = 0;                                  /* success */
    printf("report built: %zu rows, data[3]=%d index[3]=%d\n", rows, data[3], index[3]);

out:
    free(flags);                             /* free(NULL) is a safe no-op, */
    free(index);                             /* so the ladder works no matter */
    free(data);                              /* how far we got */
    return rc;
}

/* PATTERN 2: ownership transfer — the function RETURNS the heap object,
   and the CALLER owns (and frees) it. Documented in the name and comment. */
int *make_copy(const int *src, size_t n) {
    int *dst = malloc(n * sizeof *dst);
    if (!dst) return NULL;
    for (size_t i = 0; i < n; i++) dst[i] = src[i];
    return dst;                              /* ownership passes to caller */
}

/* PATTERN 3: borrow, don't own — the function uses memory it did not
   allocate and frees nothing. const documents "I won't write it either". */
long total(const int *data, size_t n) {
    long t = 0;
    for (size_t i = 0; i < n; i++) t += data[i];
    return t;
}

int main(void) {
    if (build_report(10) != 0) return 1;

    int original[5] = { 1, 2, 3, 4, 5 };
    int *mine = make_copy(original, 5);       /* I own this now */
    if (!mine) return 1;
    printf("borrowed sum: %ld\n", total(mine, 5));   /* total() borrows; frees nothing */
    free(mine);                              /* owner frees — once */
    return 0;
}
