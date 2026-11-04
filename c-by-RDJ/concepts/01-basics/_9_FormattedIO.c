// Tags: #C #Basics #Printf #Scanf #FormattedIO | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

int main(void) {
    /* printf returns the number of characters printed — CHECK IT when it matters */
    int printed = printf("%-10s|%5d|%08.3f|%c\n", "label", 42, 3.14159, 'Z');
    printf("that line had %d characters\n", printed);

    /* The safe input pattern: fgets the WHOLE line, then sscanf it.
       scanf("%d") alone leaves the newline in the buffer (the Java Scanner trap),
       and scanf("%s") overflows on long input. */
    char line[64] = "42 RDJ 3.75\n";
    int id;
    char name[32];
    double gpa;

    int converted = sscanf(line, "%d %31s %lf", &id, name, &gpa);
    if (converted == 3) {
        printf("parsed %d fields: id=%d name=%s gpa=%.2f\n", converted, id, name, gpa);
    } else {
        printf("bad input: only %d of 3 fields parsed\n", converted);
    }

    /* Widths and flags on printf */
    printf("[%10d] right-aligned\n", 123);
    printf("[%-10d] left-aligned\n", 123);
    printf("[%010d] zero-padded\n", 123);
    printf("[%.4s] truncated string\n", "truncation");
    return 0;
}
