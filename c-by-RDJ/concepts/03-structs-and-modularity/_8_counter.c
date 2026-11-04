// Tags: #C #Headers #Linking #Extern #Static | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

/* _8_counter.c — the IMPLEMENTATION of _8_counter.h's interface. */
#include "_8_counter.h"

/* 'static' here means INTERNAL LINKAGE: invisible outside this file.
   A private helper — the closest thing C has to 'private'. */
static int count = 0;        /* module-private state */

void counter_bump(void) {
    count++;
}

int counter_total(void) {
    return count;
}

void counter_reset(void) {
    count = 0;
}
