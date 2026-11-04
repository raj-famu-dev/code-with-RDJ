// Tags: #C #Headers #Linking #Build | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

/* _8_HeadersAndLinking.c — the CONSUMER. Two translation units build together. */
#include <stdio.h>
#include "_8_counter.h"

/* This file uses counter_* through the header only. 'count' itself is
   unreachable — static in _8_counter.c — which is exactly the point. */

int main(void) {
    counter_bump();
    counter_bump();
    counter_bump();
    printf("count = %d (three bumps)\n", counter_total());
    counter_reset();
    printf("after reset = %d\n", counter_total());
    return 0;
}
