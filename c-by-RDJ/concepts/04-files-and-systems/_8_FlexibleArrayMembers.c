// Tags: #C #FlexibleArrayMembers #Malloc #DynamicArrays | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>

/* The problem: a struct holding "a header + N items" needs ONE allocation.
   The C99 solution: a flexible array member — 'items[]' with no size,
   declared LAST. sizeof(struct) ignores it. */
typedef struct {
    size_t count;      /* the header */
    int items[];       /* the payload: zero-length placeholder */
} IntVec;

/* ONE malloc for header + payload: the address arithmetic is the trick. */
static IntVec *vec_new(size_t n) {
    /* sizeof(IntVec) may include padding to satisfy alignment of int —
       the offsetof formula is the portable way to size the header part. */
    size_t header = offsetof(IntVec, items);
    IntVec *v = malloc(header + n * sizeof(int));
    if (!v) return NULL;
    v->count = n;
    return v;
}

int main(void) {
    printf("sizeof(IntVec) = %zu (the flexible member adds NOTHING)\n", sizeof(IntVec));

    IntVec *v = vec_new(5);
    if (!v) return 1;
    for (size_t i = 0; i < v->count; i++) {
        v->items[i] = (int)(i * i);        /* items live right after the header */
    }
    printf("squares:");
    for (size_t i = 0; i < v->count; i++) printf(" %d", v->items[i]);
    printf("\n");

    /* The memory picture: ONE block, header immediately followed by items.
       Compare: struct { size_t count; int *items; } needs TWO allocations. */
    printf("one allocation: header at %p, items at %p (contiguous)\n",
           (void *)v, (void *)v->items);

    /* grow: realloc the WHOLE thing (header + payload move together) */
    IntVec *bigger = realloc(v, offsetof(IntVec, items) + 8 * sizeof(int));
    if (!bigger) { free(v); return 1; }
    v = bigger;
    v->count = 8;
    for (size_t i = 5; i < 8; i++) v->items[i] = (int)(i * i);
    printf("after realloc to 8:");
    for (size_t i = 0; i < 8; i++) printf(" %d", v->items[i]);
    printf("\n");

    /* one free releases everything */
    free(v);
    printf("one free. done.\n");
    return 0;
}
