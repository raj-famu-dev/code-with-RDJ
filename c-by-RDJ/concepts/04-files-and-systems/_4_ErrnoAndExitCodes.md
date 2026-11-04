# `_4_ErrnoAndExitCodes.c`

## Concept
C has no exceptions — failures are **return values**, and the details live in `errno`, a per-thread global the library sets on failure. Combined with process exit codes, this is C's entire error-reporting contract.

## The Code

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

static void read_config(const char *path) {
    FILE *f = fopen(path, "r");
    if (f == NULL) {
        fprintf(stderr, "read_config: cannot open '%s': %s\n", path, strerror(errno));
        return;
    }
    fclose(f);
    printf("read_config: '%s' opened fine\n", path);
}

int main(void) {
    read_config("_4_does_not_exist.conf");
    read_config("/root/forbidden.conf");

    errno = ENOENT;
    perror("after manual errno=ENOENT");

    printf("simulating: bad arguments would exit(2), runtime failure exit(1), success exit(0)\n");

    if (fopen("/root/forbidden.conf", "r") == NULL) {
        printf("runtime failure detected; a real CLI would return 1 here\n");
    }
    return 0;
}
```

## Line-by-Line Breakdown

### `errno`
A modifiable global (macro expanding to a per-thread slot). Library functions **set it on failure** — but **never clear it on success**. The rule that follows: **check the return value first; only then read errno.** (Java's exceptions carry their message with them; C makes you fetch it from the side.)

### `strerror(errno)` → the human message
`strerror` maps the number to a string ("No such file or directory"). The pattern `fprintf(stderr, "context: %s: %s\n", path, strerror(errno))` is the standard C error line: **what you were doing, and why it failed**.

### `perror("prefix")`
The shortcut for the same line: prints `prefix: <message>`. Good for quick tools; `strerror` when you need to control formatting.

### Two failures, two errnos
- Missing file → `ENOENT` (No such file or directory)
- No permissions → `EACCES` (Permission denied)

The same NULL return, distinguished only by `errno` — which is exactly why checking it beats printing a generic "failed".

### Exit codes: the process's verdict
`return n;` from `main` (or `exit(n)`) sets the process exit status: **0 = success**, nonzero = failure. The convention from your Python scanner project — generic failure 1, usage error 2 — is the same one used here (`EXIT_SUCCESS`/`EXIT_FAILURE` from `<stdlib.h>` for portability). Scripts and CI read `$?`; the walkthrough and tests can too.

### Why `stderr`, not `printf`
Errors belong on the error stream: separate from program output, so `demo > out.txt` keeps them visible, and pipelines don't swallow them.

## Traps
- `if (errno)` as a success test — wrong on every platform (a successful call may have left a stale errno from an earlier failure).
- `errno` values are ints; never compare to strings — use the `E*` macros.
- Forgetting `return 1` on failure — the exit code is the contract; `main` falling through returns 0 ("success") by default.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _4_ErrnoAndExitCodes.c && ./demo
echo "exit was $?"
```

## Why This Structure Exists
Return values + `errno` + exit codes make error handling *explicit at every call site* — verbose, but nothing is hidden and nothing throws from under you. Module 06's ownership ladder (goto cleanup) is how multi-resource failures are unwound under this contract.
