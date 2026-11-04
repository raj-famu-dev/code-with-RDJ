// Tags: #C #Basics #Arrays | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

int main(void) {
    /* Fixed size, decided at compile time. No bounds checking. Ever. */
    int scores[5] = { 90, 85, 77, 95, 60 };

    /* The classic length idiom: total bytes / bytes per element */
    size_t n = sizeof scores / sizeof scores[0];
    printf("length: %zu\n", n);

    int sum = 0;
    for (size_t i = 0; i < n; i++) {
        sum += scores[i];
    }
    printf("average: %.1f\n", (double)sum / (double)n);

    /* Partial init: rest are zeroed */
    int sparse[5] = { 1, 2 };
    printf("sparse: %d %d %d %d %d\n", sparse[0], sparse[1], sparse[2], sparse[3], sparse[4]);

    /* Designated initializers (C99): init by index, rest zeroed */
    int by_index[5] = { [2] = 30, [4] = 50 };
    printf("by_index: %d %d %d %d %d\n", by_index[0], by_index[1], by_index[2], by_index[3], by_index[4]);

    /* 2-D: an array of arrays, contiguous */
    int grid[2][3] = { { 1, 2, 3 }, { 4, 5, 6 } };
    printf("grid[1][2] = %d\n", grid[1][2]);
    printf("sizeof grid = %zu (2*3 ints)\n", sizeof grid);

    /* OUT OF BOUNDS IS NOT CHECKED — we do NOT run this; it is UB. */
    printf("scores[4] is the last valid index; scores[5] would be undefined behavior.\n");
    return 0;
}
