// Tags: #C #MemoryManagement #Sanitizers #ASan #UBSan | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* DEFAULT RUN: safe versions of the classic bugs, and an explanation.
   TRIGGER RUN (--trigger): deliberately buggy, caught by the sanitizers.
   This mirrors cpp-by-RDJ's memory-safety lab: bug, report, fix. */

int main(int argc, char **argv) {
    int trigger = (argc > 1 && strcmp(argv[1], "--trigger") == 0);

    if (!trigger) {
        printf("safe run: every bug below has a --trigger version.\n");
    }

    /* --- BUG 1: use-after-free ------------------------------------- */
    int *p = malloc(sizeof *p);
    if (!p) return 1;
    *p = 42;
    if (trigger) {
        /* Deliberate UB below: the compiler warns (-Wuse-after-free) and ASan
           reports it at runtime. The warning is suppressed ONLY for this block
           because the bug is the lesson. */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wuse-after-free"
        free(p);
        printf("reading *p after free: %d (UB — ASan reports heap-use-after-free)\n", *p);
#pragma GCC diagnostic pop
    } else {
        printf("use-after-free: read the value BEFORE free, never after. fixed: *p=%d\n", *p);
        free(p);
    }

    /* --- BUG 2: heap buffer overflow -------------------------------- */
    int *q = malloc(3 * sizeof *q);
    if (!q) return 1;
    if (trigger) {
        q[3] = 99;   /* index 3 in a 3-element array: one past the end */
        printf("wrote q[3] in a 3-element block (UB — ASan: heap-buffer-overflow)\n");
    } else {
        q[0] = 1; q[1] = 2; q[2] = 3;
        printf("heap overflow: only indices 0..2 are valid. fixed: q = %d %d %d\n", q[0], q[1], q[2]);
    }
    free(q);

    /* --- BUG 3: memory leak ----------------------------------------- */
    if (trigger) {
        int *leak = malloc(64 * sizeof *leak);
        if (!leak) return 1;
        leak[0] = 1;
        printf("leaked 64 ints: no free() on this path (LeakSanitizer reports at exit)\n");
    } else {
        printf("leak: every malloc pairs with a free on every path.\n");
    }

    /* --- BUG 4: double free ----------------------------------------- */
    int *d = malloc(sizeof *d);
    if (!d) return 1;
    free(d);
    if (trigger) {
        /* Deliberate UB: double free. Same suppression reasoning as above. */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wuse-after-free"
        free(d);   /* freeing the same block twice */
        printf("double free attempted (UB — ASan: attempting double-free)\n");
#pragma GCC diagnostic pop
    } else {
        printf("double free: after free, NULL the pointer — the safe pattern is free(p), p=NULL.\n");
    }
    return 0;
}
