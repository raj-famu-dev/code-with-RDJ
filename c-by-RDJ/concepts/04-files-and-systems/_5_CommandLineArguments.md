# `_5_CommandLineArguments.c`

## Concept
`main` has a second signature: `int main(int argc, char **argv)`. Arguments arrive as an array of C strings — `argv[0]` is the program name, `argv[argc]` is guaranteed NULL, and everything is **text** until you parse it.

## The Code

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    printf("argc = %d\n", argc);
    for (int i = 0; i < argc; i++) {
        printf("argv[%d] = '%s'\n", i, argv[i]);
    }
    printf("argv[argc] is %s\n", argv[argc] == NULL ? "NULL (guaranteed)" : "not NULL?!");

    if (argc < 3) {
        fprintf(stderr, "usage: %s <name> <number>\n", argv[0]);
        return 2;
    }

    printf("hello, %s\n", argv[1]);

    char *end = NULL;
    long value = strtol(argv[2], &end, 10);
    if (end == argv[2] || *end != '\0') {
        fprintf(stderr, "not a number: '%s'\n", argv[2]);
        return 2;
    }
    printf("%ld doubled is %ld\n", value, value * 2);

    for (int i = 3; i < argc; i++) {
        if (strcmp(argv[i], "--verbose") == 0) {
            printf("(verbose mode on)\n");
        } else if (strcmp(argv[i], "-n") == 0 && i + 1 < argc) {
            printf("(n = %s)\n", argv[i + 1]);
            i++;
        } else {
            fprintf(stderr, "unknown arg: '%s'\n", argv[i]);
            return 2;
        }
    }
    return 0;
}
```

## Line-by-Line Breakdown

### `int main(int argc, char **argv)`
`argc` — how many arguments; `argv` — an array of `char *` (Module 02's pointer-to-pointer: an array of string pointers). `argv[0]` is the program's name *as invoked* (`./demo`); real CLIs use it in usage messages instead of hardcoding their own name.

### `argv[argc] == NULL`
The array is NULL-terminated like every good C array — the loop `for (char **p = argv; *p; p++)` works without `argc` at all.

### Arguments are strings
`./demo RDJ 21` gives `"RDJ"` and `"21"` — the latter is two characters, not the number 21. Parsing is your job:

### `strtol(argv[2], &end, 10)` — the safe number parse
Converts as much as parses, and sets `end` to the first character it *couldn't* convert. Validation: `end == argv[2]` means **nothing** parsed ("abc"); `*end != '\0'` means **partial** garbage ("21x"). This is the C pattern your Python `argparse`'s `type=int` automates — and it never overflows silently the way `atoi` does.

### The usage error: `return 2`
The CLI convention (your Python scanner uses it too): exit 2 = the *user* gave bad input; exit 1 = runtime failure. Scripts can distinguish them.

### The hand-rolled flag loop
`--verbose` as a boolean flag; `-n value` consuming the next argument. This is what `getopt` (POSIX) automates — real tools use it; the hand-roll teaches what it's for.

## Traps
- `argv[1]` with `argc == 1` — reading past the array. Check `argc` before indexing.
- `atoi("abc")` silently returns 0 — no error, just wrong. Use `strtol` + `end` check.
- Parsing with `sscanf(argv[2], "%ld", &v)` loses the partial-parse detection that `strtol`'s `end` gives you.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _5_CommandLineArguments.c
./demo RDJ 21 --verbose -n 5
./demo                    # usage error, exit 2
./demo RDJ abc            # not a number, exit 2
echo $?                   # see the exit codes
```

## Why This Structure Exists
`argc`/`argv` is the contract between your program and the shell — the same interface your Python scanner, your Makefiles, and every Unix tool share. Parsing it safely (`strtol` + exit codes) is what makes a C program *scriptable*.
