// Tags: #C #Pointers #Strings #CharPointers | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

int main(void) {
    /* An array of char: YOUR storage, modifiable. */
    char owned[] = "Hello";
    owned[0] = 'J';
    printf("owned: %s (own bytes, safe to modify)\n", owned);

    /* A pointer to a literal: READ-ONLY bytes; writing through it is UB. */
    const char *lit = "Hello";
    printf("lit: %s (points at a read-only literal)\n", lit);

    /* Same spelling, different meanings:
         char s[] = "x"  -> copies the chars into a new array (stack)
         char *p  = "x"  -> p points at the anonymous, read-only literal      */
    printf("sizeof owned = %zu (the array), sizeof lit = %zu (the pointer)\n",
           sizeof owned, sizeof lit);

    /* Two literals may share storage (deduplication is allowed) */
    const char *a = "same";
    const char *b = "same";
    printf("a == b? %s (deduplication is allowed, never assumed)\n", (a == b) ? "yes" : "no");

    /* The loop every string function runs internally: walk to the '\0'. */
    size_t len = 0;
    while (owned[len] != '\0') {
        len++;
    }
    printf("hand-rolled strlen: %zu\n", len);

    /* Who owns what:
       - owned[] owns its bytes and dies with its scope.
       - lit owns nothing; the literal has static lifetime (whole program).
       - a malloc'd string (next topics) owns heap bytes until YOU free them. */
    printf("ownership: arrays own their bytes; pointers to literals own nothing.\n");
    return 0;
}
