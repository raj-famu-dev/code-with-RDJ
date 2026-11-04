// Tags: #C #Pointers #MemoryManagement | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

int main(void) {
    int x = 42;

    /* A pointer is a variable that holds an ADDRESS. */
    int *p = &x;          /* & takes the address of x */

    printf("x lives at %p and holds %d\n", (void *)&x, x);
    printf("p holds %p and points at %d\n", (void *)p, *p);

    /* * has two meanings: declaration ("pointer to") and dereference ("follow it") */
    *p = 99;              /* write THROUGH the pointer: x is now 99 */
    printf("after *p = 99, x = %d (same storage, reached via p)\n", x);

    /* Pointers have a size of their own — independent of what they point to */
    printf("sizeof(int*)=%zu sizeof(double*)=%zu sizeof(void*)=%zu\n",
           sizeof(int *), sizeof(double *), sizeof(void *));

    /* NULL: the "points at nothing" value. Dereferencing it is a crash (ASan catches it). */
    int *q = NULL;
    if (q == NULL) {
        printf("q is NULL — check before you dereference\n");
    }

    /* Pointer to pointer: an address of an address */
    int **pp = &p;
    printf("**pp = %d (follow twice to reach x)\n", **pp);
    return 0;
}
