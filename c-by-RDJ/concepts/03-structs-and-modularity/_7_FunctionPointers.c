// Tags: #C #FunctionPointers #Callbacks #Qsort | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* A function pointer stores the ADDRESS of a function. The syntax:
       return_type (*name)(param_types)
   The parens around *name are mandatory — without them it declares
   a function returning a pointer. */

int add(int a, int b) { return a + b; }
int mul(int a, int b) { return a * b; }

/* USE 1: pass behavior as an argument (the callback — C's polymorphism). */
int apply(int (*op)(int, int), int x, int y) {
    return op(x, y);                       /* call through the pointer */
}

/* USE 2: dispatch tables — an array of function pointers replaces a switch. */
int neg(int a, int b) { return a - b; }
int divi(int a, int b) { return b != 0 ? a / b : 0; }

/* USE 3: the comparator contract that qsort requires:
       int cmp(const void *a, const void *b) — negative/0/positive. */
int cmp_int_asc(const void *a, const void *b) {
    int x = *(const int *)a, y = *(const int *)b;
    return (x > y) - (x < y);             /* safe, overflow-free compare */
}
int cmp_int_desc(const void *a, const void *b) {
    return cmp_int_asc(b, a);             /* reuse by swapping args */
}

int main(void) {
    /* Pointers to functions: assign the function's name (no &) — it decays. */
    int (*op)(int, int) = add;
    printf("op(3, 4) = %d\n", op(3, 4));
    op = mul;
    printf("op(3, 4) = %d (same call site, different function)\n", op(3, 4));

    /* Callbacks */
    printf("apply(add, 3, 4) = %d\n", apply(add, 3, 4));
    printf("apply(mul, 3, 4) = %d\n", apply(mul, 3, 4));

    /* Dispatch table */
    int (*ops[4])(int, int) = { add, mul, neg, divi };
    const char *names[4] = { "add", "mul", "sub", "div" };
    for (int i = 0; i < 4; i++)
        printf("%s(10, 2) = %d\n", names[i], ops[i](10, 2));

    /* qsort: the standard library's own callback interface */
    int data[6] = { 42, 7, 19, 3, 88, 15 };
    qsort(data, 6, sizeof data[0], cmp_int_asc);
    printf("ascending:  %d %d %d %d %d %d\n", data[0], data[1], data[2], data[3], data[4], data[5]);
    qsort(data, 6, sizeof data[0], cmp_int_desc);
    printf("descending: %d %d %d %d %d %d\n", data[0], data[1], data[2], data[3], data[4], data[5]);
    return 0;
}
