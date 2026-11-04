// Tags: #C #FileIO #Stdio #Fopen | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

int main(void) {
    /* fopen returns a FILE* — an opaque handle to a buffered stream.
       NULL means failure: ALWAYS check. */
    FILE *f = fopen("_1_demo.txt", "w");
    if (f == NULL) {
        perror("fopen");        /* prints "fopen: <errno message>" */
        return 1;
    }
    fprintf(f, "first line\n");
    fprintf(f, "second line\n");

    /* fclose flushes buffers and releases the handle. Missing it can mean:
       - buffered data never reaches the disk
       - a leak of the handle (an OS resource, not GC'd memory) */
    if (fclose(f) != 0) {
        perror("fclose");
        return 1;
    }
    printf("wrote _1_demo.txt and closed it cleanly\n");

    /* The mode string decides everything:
       "r"  read, file must exist           "r+" read+write, file must exist
       "w"  write, TRUNCATES or creates     "w+" read+write, truncates
       "a"  append, creates if absent       "a+" read+append
       ...append "b" ("rb","wb") for binary — see topic 3. */
    FILE *in = fopen("_1_demo.txt", "r");
    if (in == NULL) { perror("fopen"); return 1; }

    char line[64];
    while (fgets(line, sizeof line, in) != NULL) {
        printf("read: %s", line);        /* line includes the '\n' */
    }
    fclose(in);

    /* A read of a missing file shows the NULL-check in action. */
    FILE *missing = fopen("_1_does_not_exist.txt", "r");
    printf("fopen of a missing file: %s (NULL — checked, no crash)\n",
           missing == NULL ? "returned NULL" : "succeeded?!");
    return 0;
}
