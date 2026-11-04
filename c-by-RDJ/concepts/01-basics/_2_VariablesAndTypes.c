// Tags: #C #Basics #Variables #DataTypes | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdint.h>
#include <limits.h>
#include <stdbool.h>

int main(void) {
    int    a = 42;            /* at least 16 bits; 32 on this platform */
    long   big = 9000000000L; /* at least 32 bits; 64 here */
    double d = 3.14;
    char   c = 'A';           /* a single byte holding a character code */
    bool   flag = true;       /* C99 bool via <stdbool.h> */
    unsigned u = 4000000000u; /* no sign bit: double the positive range */

    /* Fixed-width types: what serious code actually uses */
    int32_t exact32 = 2147483647;
    int64_t exact64 = 9000000000000000000LL;
    uint8_t one_byte = 255;

    printf("int=%d long=%ld double=%.2f char=%c bool=%d unsigned=%u\n",
           a, big, d, c, flag, u);
    printf("int32=%d int64=%lld uint8=%u\n", exact32, (long long)exact64, one_byte);
    printf("INT_MAX=%d INT_MIN=%d UINT_MAX=%u\n", INT_MAX, INT_MIN, UINT_MAX);
    printf("CHAR_BIT=%d (a byte has %d bits on this machine)\n", CHAR_BIT, CHAR_BIT);
    return 0;
}
