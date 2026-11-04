// Tags: #C #DataStructures #DynamicArray #Realloc | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>

/* The dynamic array: what std::vector, ArrayList and Python's list all are.
   A heap block + count + capacity, DOUBLING when full. */

typedef struct {
    int *data;
    size_t count;     /* how many are in use        */
    size_t capacity;  /* how many slots are allocated */
    size_t copies;    /* MEASUREMENT: data moves during growth */
} DArray;

static int da_init(DArray *a, size_t start_cap) {
    a->data = malloc(start_cap * sizeof *a->data);
    if (!a->data) return -1;
    a->count = 0;
    a->capacity = start_cap;
    a->copies = 0;
    return 0;
}

static void da_free(DArray *a) {
    free(a->data);
    a->data = NULL;
    a->count = a->capacity = 0;
}

/* Append. If full: DOUBLE the capacity, realloc (which may move the block —
   the copies are the measured cost of growth). */
static int da_push(DArray *a, int value) {
    if (a->count == a->capacity) {
        size_t new_cap = a->capacity * 2;
        int *bigger = realloc(a->data, new_cap * sizeof *bigger);
        if (!bigger) return -1;              /* original still valid: caller keeps ownership */
        a->copies += a->capacity;            /* MEASURE: every existing element moved */
        a->data = bigger;
        a->capacity = new_cap;
    }
    a->data[a->count++] = value;
    return 0;
}

static int da_get(const DArray *a, size_t i) {
    return a->data[i];                       /* caller checks bounds: i < count */
}

int main(void) {
    DArray a;
    if (da_init(&a, 4) != 0) return 1;

    /* Push 100,000 values; count the element-copies caused by growth. */
    const size_t N = 100000;
    for (size_t i = 0; i < N; i++) {
        if (da_push(&a, (int)(i % 1000)) != 0) return 1;
    }
    printf("pushed %zu values: count=%zu capacity=%zu\n", N, a.count, a.capacity);
    printf("element-copies during growth: %zu total (%.2f per push)\n",
           a.copies, (double)a.copies / (double)N);
    printf("=> amortized O(1): doubling makes each push's average cost constant\n");

    /* Random access is O(1) — the array's superpower. */
    printf("da_get(&a, 42) = %d (index arithmetic only)\n", da_get(&a, 42));

    /* The amortized argument, in numbers:
       growing 4 -> 8 -> ... -> 131072 copies each element ~log2(N/4) times TOTAL,
       which is LESS than N. Compare: growing by +1 each time = O(N^2) copies. */
    printf("a +1-sized growth would copy ~%zu elements; doubling copied %zu\n",
           N * N / 2, a.copies);

    da_free(&a);
    printf("freed.\n");
    return 0;
}
