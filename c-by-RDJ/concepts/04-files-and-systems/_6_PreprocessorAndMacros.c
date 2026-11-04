// Tags: #C #Preprocessor #Macros #IncludeGuards | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

/* The preprocessor runs BEFORE the compiler and does TEXT SUBSTITUTION.
   Macros are named text replacements — no types, no scope, no evaluation. */

/* 1. Object-like macro: constant alias */
#define MAX_NAME 32

/* 2. Function-like macro: BEWARE — it is text, not a function.
   The classic bug: MAX(a,b) expands literally, so a+1 breaks it. */
#define MAX_BROKEN(a, b) a > b ? a : b
/* The fix: FULLY parenthesize everything. */
#define MAX(a, b) ((a) > (b) ? (a) : (b))

/* 3. do/while(0): make a macro behave like ONE statement (semicolon-safe) */
#define LOG_ERROR(msg) do { fprintf(stderr, "[error] %s:%d %s\n", __FILE__, __LINE__, msg); } while (0)

/* 4. Predefined macros: the compiler's facts about THIS compilation */
/*    __FILE__, __LINE__, __DATE__, __TIME__, __STDC_VERSION__ */

/* 5. Conditional compilation: build-time switches */
#define DEBUG_BUILD 1

/* 6. Stringification and concatenation */
#define STRINGIFY(x) #x                     /* x -> "x" */
#define CONCAT(a, b) a##b                   /* pieces -> one token */

int main(void) {
    printf("__FILE__ = %s, __LINE__ = %d\n", __FILE__, __LINE__);
    printf("__STDC_VERSION__ = %ld (C17 is 201710)\n", __STDC_VERSION__);

    int x = 10, y = 5;
    printf("MAX(x, y) = %d\n", MAX(x, y));

    /* Why MAX_BROKEN fails: '10 + 1 > 5 ? 10 + 1 : 5' parses as '(10+1)>5...'
       — precedence chaos. The parenthesized version is immune. */
    printf("MAX(x + 1, y) = %d (parenthesized macro survives precedence)\n", MAX(x + 1, y));

    LOG_ERROR("a demo error with file and line");

#if DEBUG_BUILD
    printf("debug build: DEBUG_BUILD was 1 at preprocess time\n");
#else
    printf("release build\n");
#endif

    printf("STRINGIFY(42) = %s\n", STRINGIFY(42));
    int helloworld = 77;   /* the macro concatenates to THIS variable's name */
    printf("CONCAT(hello, world) = %d\n", CONCAT(hello, world));
    return 0;
}
