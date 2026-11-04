# `_1_FileOpenAndClose.c`

## Concept
File I/O starts with the `FILE *` handle: `fopen` to get it, `fclose` to release it, and a NULL check between them that is **not optional**. Everything else in this module is built on this pattern.

## The Code

```c
#include <stdio.h>

int main(void) {
    FILE *f = fopen("_1_demo.txt", "w");
    if (f == NULL) {
        perror("fopen");
        return 1;
    }
    fprintf(f, "first line\n");
    fprintf(f, "second line\n");
    if (fclose(f) != 0) {
        perror("fclose");
        return 1;
    }
    printf("wrote _1_demo.txt and closed it cleanly\n");

    FILE *in = fopen("_1_demo.txt", "r");
    if (in == NULL) { perror("fopen"); return 1; }

    char line[64];
    while (fgets(line, sizeof line, in) != NULL) {
        printf("read: %s", line);
    }
    fclose(in);

    FILE *missing = fopen("_1_does_not_exist.txt", "r");
    printf("fopen of a missing file: %s (NULL — checked, no crash)\n",
           missing == NULL ? "returned NULL" : "succeeded?!");
    return 0;
}
```

## Line-by-Line Breakdown

### `FILE *f = fopen(path, "w")`
`FILE` is an **opaque struct** — you never see its fields; you hold a pointer to one. The `w` mode creates/truncates. The handle owns a buffer, the OS file descriptor, and the stream's error state.

### The NULL check
`fopen` can fail for a dozen reasons (missing file, no permissions, no disk). It reports failure with **NULL, not an exception** — an unchecked NULL becomes a crash in the first `fprintf`. `perror` prints the reason from `errno` (topic 4).

### `fclose` returns a value too
It flushes the buffer — and the flush can fail. Checking it matters for files you just wrote: a clean exit status on unflushed data is a lie. `fclose(NULL)` is UB, so the NULL-check-before-use discipline covers it.

### The mode string
| Mode | Meaning |
|---|---|
| `"r"` | read; must exist |
| `"w"` | write; **truncates** or creates |
| `"a"` | append; creates if absent |
| `"r+"` / `"w+"` / `"a+"` | read+write variants |
| suffix `b` (`"rb"`, `"wb"`) | binary mode (topic 3) |

`"w"` silently destroys an existing file — the most destructive two characters in the standard library.

### `fgets` loop
The canonical line-reading loop: `fgets` reads at most `sizeof line - 1` bytes, stops at newline (kept!), and returns NULL at end-of-file. Bounded by the buffer size — this is the safe reader `gets` never was (Module 01).

## Traps
- Forgetting `fclose` on a write path: buffered bytes lost (the file is empty or short).
- Double `fclose` — undefined behavior.
- Using the `FILE *` after `fclose` — a dangling handle (use-after-free's sibling).

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _1_FileOpenAndClose.c && ./demo
```

## Why This Structure Exists
A `FILE *` wraps the OS's raw file descriptor in a *buffered* stream — C's key performance decision (batch the syscalls). The handle/NULL-check/close pattern is the resource discipline that C++'s RAII destructors automate and Python's `with` automates; in C, it's yours to run by hand.
