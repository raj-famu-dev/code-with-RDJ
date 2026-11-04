// Tags: #C #Argv #CommandLine #CLI | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* argc = argument count. argv = array of C-string pointers:
       argv[0]      the program name (or something the OS chose)
       argv[1..]    the arguments, as STRINGS
       argv[argc]   always NULL
   Everything arrives as text — numbers need parsing, and you own the check. */

int main(int argc, char **argv) {
    printf("argc = %d\n", argc);
    for (int i = 0; i < argc; i++) {
        printf("argv[%d] = '%s'\n", i, argv[i]);
    }
    printf("argv[argc] is %s\n", argv[argc] == NULL ? "NULL (guaranteed)" : "not NULL?!");

    if (argc < 3) {
        fprintf(stderr, "usage: %s <name> <number>\n", argv[0]);
        return 2;                                  /* 2: usage error, the CLI convention */
    }

    /* argv[1] is a string; use it as one */
    printf("hello, %s\n", argv[1]);

    /* argv[2] LOOKS like a number but is text: parse and validate */
    char *end = NULL;
    long value = strtol(argv[2], &end, 10);         /* base 10 */
    if (end == argv[2] || *end != '\0') {
        fprintf(stderr, "not a number: '%s'\n", argv[2]);
        return 2;
    }
    printf("%ld doubled is %ld\n", value, value * 2);

    /* Flags: hand-rolled option loop (what getopt/argparse automate) */
    for (int i = 3; i < argc; i++) {
        if (strcmp(argv[i], "--verbose") == 0) {
            printf("(verbose mode on)\n");
        } else if (strcmp(argv[i], "-n") == 0 && i + 1 < argc) {
            printf("(n = %s)\n", argv[i + 1]);
            i++;                                    /* consume the value */
        } else {
            fprintf(stderr, "unknown arg: '%s'\n", argv[i]);
            return 2;
        }
    }
    return 0;
}
