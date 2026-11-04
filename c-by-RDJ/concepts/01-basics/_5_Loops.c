// Tags: #C #Basics #Loops | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

int main(void) {
    /* for: known trip count */
    int sum = 0;
    for (int i = 1; i <= 5; i++) {
        sum += i;
    }
    printf("1+2+3+4+5 = %d\n", sum);

    /* while: condition first — may run zero times */
    int n = 5, fact = 1;
    while (n > 1) {
        fact *= n--;
    }
    printf("5! = %d\n", fact);

    /* do-while: body first — always runs at least once */
    int countdown = 3;
    do {
        printf("countdown: %d\n", countdown--);
    } while (countdown > 0);

    /* break leaves the loop; continue jumps to the next pass */
    for (int i = 1; i <= 6; i++) {
        if (i == 3) continue;   /* skip 3 */
        if (i == 5) break;      /* stop at 5 */
        printf("i=%d\n", i);
    }
    return 0;
}
