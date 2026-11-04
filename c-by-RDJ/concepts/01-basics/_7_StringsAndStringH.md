# `_7_StringsAndStringH.c`

## Concept
C has **no string type**. A "string" is a `char` array whose end is marked by a `'\0'` byte — everything in `<string.h>` works by scanning for that byte. Every buffer-overflow security bug in history lives at this boundary.

## The Code

```c
#include <stdio.h>
#include <string.h>

int main(void) {
    char name[6] = { 'R', 'D', 'J', '\0' };
    char greet[] = "Hello";
    printf("%s %s\n", greet, name);

    printf("strlen(\"Hello\") = %zu (NOT counting the '\\0')\n", strlen("Hello"));
    printf("sizeof greet = %zu (including the '\\0')\n", sizeof greet);

    char copy[16];
    strcpy(copy, greet);
    printf("copy: %s\n", copy);
    printf("strcmp(copy, \"Hello\") = %d (0 means equal)\n", strcmp(copy, "Hello"));
    printf("strncmp(copy, \"Hello!\", 5) = %d (first 5 chars match)\n", strncmp(copy, "Hello!", 5));

    char full[32];
    strcpy(full, "code-");
    strcat(full, "with-RDJ");
    printf("full: %s\n", full);
    printf("strchr(full, '-') finds the first '-': %s\n", strchr(full, '-'));
    printf("strstr(full, \"with\") : %s\n", strstr(full, "with"));

    char line[16];
    snprintf(full, sizeof full, "safe-format");
    printf("snprintf result: %s\n", full);
    return 0;
}
```

## Line-by-Line Breakdown

### `char greet[] = "Hello"`
The compiler counts 6 bytes: `H e l l o` plus the terminator. A string literal like `"Hello"` is an anonymous read-only array in memory — the `'\0'` is always included.

### `strlen` vs `sizeof`
`strlen` counts characters *before* the `'\0'` (5). `sizeof` on the array counts *all* bytes (6). On a `char *` pointing to a literal, `sizeof` gives the pointer size (8) — a classic trap.

### `strcpy` / `strcat`
Copy/append, scanning until `'\0'`. **Neither knows your destination's size.** If the source is longer than the destination, you overwrite adjacent memory — the buffer overflow. `strncpy`/`strncat` take a bound (with their own footguns); `snprintf` is the modern safe copy.

### `strcmp` / `strncmp`
Return 0 when equal (inverted from intuition!), negative/positive for less/greater. `strncmp` compares at most N bytes — bounded.

### `strchr` / `strstr`
Find first occurrence of a character / substring; return a pointer *into* the string, or `NULL` if absent — always check for `NULL`.

### `snprintf`
`sprintf`'s bounded sibling: writes at most `sizeof full` bytes (including the `'\0'`). The default choice for building strings.

## Traps
- `gets()` is removed from C11 for a reason: no size, no safety. Use `fgets` (Module 04).
- Forgetting the `'\0'` when building a string by hand makes `strlen` run off the end.
- `char *s = "hi"; s[0] = 'H';` — writing to a literal is undefined behavior (literals are read-only).

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _7_StringsAndStringH.c && ./demo
```

## Why This Structure Exists
A string as "array + terminator" needs zero metadata and matches what text I/O actually moves — bytes until a sentinel. The cost is that every operation's safety depends on the buffer's size, which C makes *your* job.
