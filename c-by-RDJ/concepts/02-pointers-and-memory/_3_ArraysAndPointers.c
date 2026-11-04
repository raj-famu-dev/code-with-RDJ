// Tags: #C #Pointers #Arrays #Decay | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

/* The function receives a POINTER, not the array. The length is gone. */
int sum_ints(const int *data, size_t n) {
    int total = 0;
    for (size_t i = 0; i < n; i++) {
        total += data[i];
    }
    return total;
}

/* int a[2][3] is an array of arrays (one contiguous block, real 2-D). */
void grid_demo(void) {
    int grid[2][3] = { { 1, 2, 3 }, { 4, 5, 6 } };
    printf("grid[1][2] = %d, sizeof grid = %zu\n", grid[1][2], sizeof grid);
}

/* int *m[3] is an array of 3 POINTERS — rows can live anywhere (jagged). */
void jagged_demo(void) {
    int row0[] = { 1, 2 };
    int row1[] = { 3, 4, 5 };
    int *m[2] = { row0, row1 };
    printf("jagged m[1][2] = %d (rows of different lengths)\n", m[1][2]);
}

int main(void) {
    int a[5] = { 1, 2, 3, 4, 5 };

    /* DECAY: in most expressions, 'a' becomes '&a[0]' */
    int *p = a;
    printf("*p = %d, but sizeof a = %zu (only the ARRAY keeps its size)\n", *p, sizeof a);
    printf("sizeof p = %zu (a pointer is just 8 bytes)\n", sizeof p);

    /* sizeof is the exception to decay — that's how the length idiom works,
       but ONLY where the array itself is still visible. */
    printf("sum = %d\n", sum_ints(a, sizeof a / sizeof a[0]));

    grid_demo();
    jagged_demo();
    return 0;
}
