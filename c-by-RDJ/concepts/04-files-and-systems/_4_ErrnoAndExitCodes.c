// Tags: #C #Errno #ErrorHandling #ExitCodes | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

/* C has no exceptions. Errors travel through RETURN VALUES, and details
   travel through 'errno' — a per-thread global that library functions set
   on failure. */

/* Rule 1: errno is only meaningful AFTER a failure return. It is NOT
   cleared on success — check the return value FIRST, then errno. */
static void read_config(const char *path) {
    FILE *f = fopen(path, "r");
    if (f == NULL) {
        /* strerror turns the errno number into a human message */
        fprintf(stderr, "read_config: cannot open '%s': %s\n", path, strerror(errno));
        return;
    }
    fclose(f);
    printf("read_config: '%s' opened fine\n", path);
}

int main(void) {
    /* Demonstrate two distinct failure reasons through the same code path */
    read_config("_4_does_not_exist.conf");   /* ENOENT: no such file */
    read_config("/root/forbidden.conf");      /* EACCES: permission denied */

    /* perror: prints "prefix: <message>" from the current errno */
    errno = ENOENT;
    perror("after manual errno=ENOENT");

    /* EXIT CODES: the process's one-line verdict for scripts and CI.
       0 = success; nonzero = failure (1 = generic; 2 = usage error). */
    printf("simulating: bad arguments would exit(2), runtime failure exit(1), success exit(0)\n");

    if (fopen("/root/forbidden.conf", "r") == NULL) {
        printf("runtime failure detected; a real CLI would return 1 here\n");
    }
    return 0;
}
