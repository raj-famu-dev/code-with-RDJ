// Tags: #C #Basics #Strings #StringH | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <string.h>

int main(void) {
    /* A C string is a char array whose end is marked by a '\0' byte. */
    char name[6] = { 'R', 'D', 'J', '\0' };   /* rest zeroed */
    char greet[] = "Hello";                   /* compiler counts 6: H e l l o \0 */
    printf("%s %s\n", greet, name);

    printf("strlen(\"Hello\") = %zu (NOT counting the '\\0')\n", strlen("Hello"));
    printf("sizeof greet = %zu (including the '\\0')\n", sizeof greet);

    /* Copying and comparing */
    char copy[16];
    strcpy(copy, greet);                      /* buffer MUST be big enough: no check */
    printf("copy: %s\n", copy);
    printf("strcmp(copy, \"Hello\") = %d (0 means equal)\n", strcmp(copy, "Hello"));

    /* The safe compare: strncmp bounds the comparison */
    printf("strncmp(copy, \"Hello!\", 5) = %d (first 5 chars match)\n", strncmp(copy, "Hello!", 5));

    /* Concatenation and searching */
    char full[32];
    strcpy(full, "code-");
    strcat(full, "with-RDJ");
    printf("full: %s\n", full);
    printf("strchr(full, '-') finds the first '-': %s\n", strchr(full, '-'));
    printf("strstr(full, \"with\") : %s\n", strstr(full, "with"));

    /* WHY gets() IS BANNED: it cannot know the buffer size, so overflow
       is unavoidable with long input. fgets() takes the size and is safe. */
    snprintf(full, sizeof full, "safe-format");   /* bounded sprintf */
    printf("snprintf result: %s\n", full);
    return 0;
}
