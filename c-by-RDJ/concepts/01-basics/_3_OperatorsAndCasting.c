// Tags: #C #Basics #Operators #Casting #IntegerOverflow | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

int main(void) {
    /* Integer division truncates; mixed int/double promotes to double */
    int seven = 7, two = 2;
    printf("7 / 2        = %d   (truncated, NOT 3.5)\n", seven / two);
    printf("7 %% 2        = %d   (remainder)\n", seven % two);
    printf("7.0 / 2      = %.1f (int promoted to double)\n", 7.0 / two);
    printf("(double)7/2  = %.1f (cast first, then divide)\n", (double)seven / two);

    /* Integer promotion: small types are widened to int before arithmetic */
    char c = 100;
    printf("char 100 + char 100 = %d (promoted to int, no overflow)\n", c + c);

    /* Unsigned wraparound is DEFINED; signed overflow is UNDEFINED BEHAVIOR */
    unsigned u = 4294967295u;          /* UINT_MAX */
    printf("UINT_MAX + 1 = %u (unsigned wraps: defined behavior)\n", u + 1);

    /* Signed overflow is UB: we do NOT run it. We show the boundary instead. */
    int im = 2147483647;              /* INT_MAX */
    printf("INT_MAX = %d; adding 1 to it is UNDEFINED (not run here)\n", im);
    printf("Use -fsanitize=undefined to catch it when it happens by accident.\n");
    return 0;
}
