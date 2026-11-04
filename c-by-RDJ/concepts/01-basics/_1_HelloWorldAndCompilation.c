// Tags: #C #Basics #HelloWorld | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

int main(void) {
    printf("Hello, World!\n");
    printf("sizeof: char=%zu short=%zu int=%zu long=%zu pointer=%zu\n",
           sizeof(char), sizeof(short), sizeof(int), sizeof(long), sizeof(void *));
    return 0;
}
