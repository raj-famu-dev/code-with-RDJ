// Tags: #C #Basics #ControlFlow #Switch | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

int main(void) {
    int score = 72;

    /* if / else if / else: conditions are int (0 = false, nonzero = true) */
    if (score >= 90) {
        printf("grade A\n");
    } else if (score >= 60) {
        printf("grade: pass (%d)\n", score);
    } else {
        printf("grade: fail\n");
    }

    /* switch: integer/char/enum ONLY; cases are labels, not blocks */
    int day = 3;
    switch (day) {
    case 1:  printf("Mon\n"); break;
    case 2:  printf("Tue\n"); break;
    case 3:  printf("Wed\n"); break;
    case 6:  /* fall-through is INTENTIONAL and common: */
    case 7:  printf("weekend\n"); break;
    default: printf("unknown day\n"); break;
    }
    return 0;
}
