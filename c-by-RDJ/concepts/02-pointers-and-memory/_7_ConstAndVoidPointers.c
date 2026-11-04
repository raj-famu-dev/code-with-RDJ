// Tags: #C #Pointers #Const #VoidPointer | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>

/* const left of the *: the POINTED-TO data is read-only */
void print_ints(const int *data, size_t n) {
    for (size_t i = 0; i < n; i++) printf("%d ", data[i]);
    printf("\n");
}

/* const right of the *: the POINTER itself is read-only */
void fixed_view(int *const p) {
    *p = 5;            /* allowed: pointee is writable */
    /* p = NULL; */    /* forbidden: p is const */
    printf("int *const: can write *p (%d), cannot move p\n", *p);
}

/* void *: a generic pointer — no type info at the far end. */
int main(void) {
    int a[3] = { 1, 2, 3 };
    print_ints(a, 3);              /* const int* accepts int* silently (widening) */

    int x = 1;
    fixed_view(&x);

    /* void * can hold ANY object address... */
    void *v = a;
    printf("void *v holds the array address: %p\n", (void *)v);

    /* ...but you cannot dereference or do arithmetic on it (no element size) */
    /* printf("%d\n", *v);          ERROR: void is not an object type */
    /* v + 1;                       ERROR: arithmetic needs a size */

    /* To use it, cast back to what you know it is: */
    int *back = v;
    printf("cast back: %d %d\n", back[0], back[1]);

    /* malloc returns void * — implicit conversion to any object pointer */
    double *d = malloc(4 * sizeof *d);
    if (!d) return 1;
    d[0] = 2.5;
    printf("malloc's void* became double*: %.1f\n", d[0]);
    free(d);

    /* The const ladder, read right to left: */
    const int *p1;        /* pointer to const int   (can move p1, can't write *p1) */
    int *const p2 = &x;   /* const pointer to int   (can write *p2, can't move p2)  */
    const int *const p3 = &x;  /* const pointer to const int (neither) */
    (void)p1; (void)p2; (void)p3;
    printf("const ladder: [const T*] movable-readonly, [T* const] fixed-writable, [const T*const] both locked\n");
    return 0;
}
