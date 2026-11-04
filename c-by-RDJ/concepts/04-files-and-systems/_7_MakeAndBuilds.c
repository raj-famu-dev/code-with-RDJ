// Tags: #C #Make #Makefile #Build | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

/* This topic's real content is the Makefile (_7_Makefile) — this program
   is what it builds. Run:  make -f _7_Makefile   */

#include <stdio.h>

int main(void) {
    printf("built by make from _7_Makefile\n");
    printf("the Makefile rule for this file recompiles it only when it changes\n");
    return 0;
}
