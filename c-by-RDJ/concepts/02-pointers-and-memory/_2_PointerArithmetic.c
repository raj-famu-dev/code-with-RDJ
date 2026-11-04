// Tags: #C #Pointers #PointerArithmetic | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

int main(void) {
    int a[5] = { 10, 20, 30, 40, 50 };

    /* Pointer arithmetic moves in ELEMENTS, not bytes. */
    int *p = a;                    /* a decays to &a[0] */
    printf("*p = %d\n", *p);       /* 10 */
    printf("*(p+1) = %d\n", *(p + 1));   /* 20: +1 means +sizeof(int) BYTES */
    printf("*(p+3) = %d\n", *(p + 3));   /* 40 */

    /* a[i] is literally defined as *(a + i) — the subscript is sugar. */
    printf("a[2] = %d and *(a+2) = %d — the same thing\n", a[2], *(a + 2));
    printf("2[a] = %d — commutative addition, legal and unidiomatic\n", 2[a]);

    /* ++ moves the pointer itself; pointer subtraction gives element distance */
    int *start = a;
    int *end = &a[4];
    printf("distance a..a[4] = %td elements (ptrdiff_t)\n", end - start);
    printf("byte distance would be %td * %zu = %zu\n", end - start, sizeof(int),
           (size_t)(end - start) * sizeof(int));

    /* One-past-the-end is LEGAL to compute — and only to compute. */
    int *one_past = a + 5;
    printf("a+5 = %p (one-past-the-end: comparable, NOT dereferenceable)\n", (void *)one_past);

    /* Pointer comparison: only meaningful within the same array */
    printf("p < end? %s\n", (a < end) ? "yes" : "no");
    return 0;
}
