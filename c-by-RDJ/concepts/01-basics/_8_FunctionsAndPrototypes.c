// Tags: #C #Basics #Functions #Prototypes | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

/* PROTOTYPE: a promise to the compiler that this function exists.
   Without it (or with the definition AFTER main), the compiler cannot
   check your call — C99 made implicit declarations an error. */
int add(int a, int b);
void swap_fail(int a, int b);
void swap_works(int *a, int *b);

/* In real projects the prototypes live in a .h file and the definitions
   in a .c file — that split is Module 03's topic 8. */

int main(void) {
    printf("add(2, 3) = %d\n", add(2, 3));

    int x = 1, y = 2;
    swap_fail(x, y);              /* copies! x and y are unchanged */
    printf("after swap_fail:  x=%d y=%d\n", x, y);

    swap_works(&x, &y);           /* pass ADDRESSES: the function can reach the originals */
    printf("after swap_works: x=%d y=%d\n", x, y);
    return 0;
}

int add(int a, int b) {
    return a + b;
}

void swap_fail(int a, int b) {
    int tmp = a; a = b; b = tmp;  /* swaps the COPIES; caller sees nothing */
}

void swap_works(int *a, int *b) {
    int tmp = *a; *a = *b; *b = tmp;   /* swaps through the addresses */
}
