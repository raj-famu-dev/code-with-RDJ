# `_9_FormattedIO.c`

## Concept
`printf` and `scanf`: C's formatted I/O. The specifiers are the same ones Java's `printf` borrowed — C invented them. The discipline here: **check return values** and use the safe input pattern (`fgets` + `sscanf`), because the unsafe ones are the classic bugs.

## The Code

```c
#include <stdio.h>

int main(void) {
    int printed = printf("%-10s|%5d|%08.3f|%c\n", "label", 42, 3.14159, 'Z');
    printf("that line had %d characters\n", printed);

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

    printf("[%10d] right-aligned\n", 123);
    printf("[%-10d] left-aligned\n", 123);
    printf("[%010d] zero-padded\n", 123);
    printf("[%.4s] truncated string\n", "truncation");
    return 0;
}
```

## Line-by-Line Breakdown

### `printf` return value
Number of characters printed, or negative on error. Almost always ignored — but on a file or socket it matters (Module 04).

### The format specifiers
| Specifier | Argument type |
|---|---|
| `%d` | `int` |
| `%ld` / `%lld` | `long` / `long long` |
| `%u` | `unsigned int` |
| `%f` / `%.2f` | `double` |
| `%c` | `char` (int, really) |
| `%s` | `char *` (a `'\0'`-terminated string) |
| `%zu` | `size_t` |
| `%p` | pointer, for debugging |

A mismatch is undefined behavior — the compiler checks `printf` format strings against arguments only when it can see them (warn with `-Wformat`).

### Widths and flags
`%5d` (pad to 5, right), `%-5d` (left), `%08.3f` (zero-pad to 8 total, 3 decimals), `%.4s` (at most 4 chars of string). Same grammar Java's `String.format` uses.

### The safe input pattern: `fgets` + `sscanf`
`scanf("%d", &x)` parses from a *stream* and leaves whatever follows (including the newline) in the buffer — the Java `Scanner` trap, but sharper. And `scanf("%s")` writes unbounded input into a bounded array — a buffer overflow.

The fix: read the whole line with `fgets(line, sizeof line, stdin)`, then parse the string with `sscanf` — where you can **bound the string** with `%31s` (31 chars + `'\0'` into a 32-byte buffer) and count conversions.

### `sscanf` return value
The number of fields successfully converted — check it against what you expected before using the variables.

## Traps
- `scanf` needs `&` on everything except arrays (`name` is already an address).
- `"%s"` without a width is an overflow; `"%d"` with a non-number in the input matches zero fields — infinite-loop hazard.
- Never `fflush(stdin)` — undefined; flush output, not input.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _9_FormattedIO.c && ./demo
```

## Why This Structure Exists
One format mini-language serves both directions (`printf`/`scanf`) and both targets (streams and strings) — and its return values are the error-handling contract in a language without exceptions.
