// Tags: #C #MemoryManagement #Malloc #StackVsHeap | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>

int main(void) {
    /* STACK: automatic storage. Allocation is one stack-pointer move;
       deallocation happens at scope exit. Fast, small (~8 MB), LIFO. */
    int on_stack[100];
    on_stack[0] = 1;
    printf("stack: 100 ints, %zu bytes, freed automatically at scope exit\n",
           sizeof on_stack);

    /* HEAP: dynamic storage. YOU request, YOU free. Lives beyond scopes. */
    int *on_heap = malloc(100 * sizeof *on_heap);
    if (on_heap == NULL) {                  /* malloc CAN fail — always check */
        fprintf(stderr, "allocation failed\n");
        return 1;
    }
    on_heap[0] = 2;
    printf("heap: 100 ints at %p, alive until free()\n", (void *)on_heap);

    /* calloc: allocates AND zeroes */
    int *zeroed = calloc(100, sizeof *zeroed);
    if (zeroed) {
        printf("calloc: first element is %d (zeroed)\n", zeroed[0]);
        free(zeroed);
    }

    /* realloc: grow/shrink an existing block (may move it!) */
    int *grown = realloc(on_heap, 200 * sizeof *grown);
    if (grown == NULL) {
        /* on_heap is STILL VALID if realloc fails — free the original */
        free(on_heap);
        fprintf(stderr, "realloc failed\n");
        return 1;
    }
    on_heap = grown;
    printf("realloc: now 200 ints at %p (contents preserved, address may differ)\n",
           (void *)on_heap);

    free(on_heap);        /* exactly once... */
    on_heap = NULL;       /* ...then NULL it: free(NULL) is safe, double-free is UB */
    printf("freed. free(NULL) is a safe no-op; that's why we NULL pointers.\n");
    return 0;
}
