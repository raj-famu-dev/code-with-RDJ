# `_6_MemoryBugsAndSanitizers.c`

## Concept
The four classic heap bugs — use-after-free, heap-buffer-overflow, leak, double-free — each shown as a safe version (default run), a buggy version (`--trigger`), and the sanitizer report the buggy one produces. This file is C's twin of `cpp-by-RDJ/project-02-memory-safety-lab`.

## The Code

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    int trigger = (argc > 1 && strcmp(argv[1], "--trigger") == 0);

    int *p = malloc(sizeof *p);
    if (!p) return 1;
    *p = 42;
    if (trigger) {
        free(p);
        printf("reading *p after free: %d (UB — ASan reports heap-use-after-free)\n", *p);
    } else {
        printf("use-after-free: read the value BEFORE free, never after. fixed: *p=%d\n", *p);
        free(p);
    }

    int *q = malloc(3 * sizeof *q);
    if (!q) return 1;
    if (trigger) {
        q[3] = 99;
        printf("wrote q[3] in a 3-element block (UB — ASan: heap-buffer-overflow)\n");
    } else {
        q[0] = 1; q[1] = 2; q[2] = 3;
        printf("heap overflow: only indices 0..2 are valid. fixed: q = %d %d %d\n", q[0], q[1], q[2]);
    }
    free(q);

    if (trigger) {
        int *leak = malloc(64 * sizeof *leak);
        if (!leak) return 1;
        leak[0] = 1;
        printf("leaked 64 ints: no free() on this path (LeakSanitizer reports at exit)\n");
    } else {
        printf("leak: every malloc pairs with a free on every path.\n");
    }

    int *d = malloc(sizeof *d);
    if (!d) return 1;
    free(d);
    if (trigger) {
        free(d);
        printf("double free attempted (UB — ASan: attempting double-free)\n");
    } else {
        printf("double free: after free, NULL the pointer — free(p), p=NULL.\n");
    }
    return 0;
}
```

## Line-by-Line Breakdown

### The `--trigger` switch
Bugs are opt-in: the default run demonstrates the *fixed* pattern and exits 0; the trigger run commits the bug and lets the sanitizer catch it. This keeps the file runnable in CI while teaching failure.

### BUG 1: use-after-free
`free(p)` returns the block to the allocator, but the *pointer* still holds the address. Reading `*p` afterward is undefined: the bytes may be unchanged, overwritten, or the read may abort. ASan poisons freed blocks on purpose — the report says `heap-use-after-free` with the free and alloc stack traces.

### BUG 2: heap-buffer-overflow
`q[3]` in a 3-element block writes past the end — corrupting allocator metadata or neighboring allocations. ASan's redzones (poisoned bytes around every allocation) catch it on the spot: `heap-buffer-overflow`.

### BUG 3: memory leak
`malloc` with no matching `free` on *some* path. The program may run fine; the memory is simply never returned. LeakSanitizer prints a report at exit with the allocation's stack trace.

### BUG 4: double-free
The allocator's bookkeeping is already updated — the second `free` corrupts it. glibc aborts with "double free detected"; ASan says `attempting double-free`. The fix pattern is `free(p); p = NULL;` — `free(NULL)` is a no-op, so a second free of a NULLed pointer is harmless.

## Reading a sanitizer report
```
==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x602000000010
WRITE of size 4 at 0x602000000010 thread T0
    #0 0x... in main /path/_6_MemoryBugsAndSanitizers.c:37
0x602000000010 is located 0 bytes to the right of 12-byte region [0x602000000004,0x602000000010)
allocated by thread T0 here:
    #0 0x... in malloc
    #1 0x... in main /path/_6_MemoryBugsAndSanitizers.c:30
```
Three things to read: the bug type, the faulting line (`#0`), and the allocation site (`allocated by`) with its line. ASan is telling you a story: who allocated it, who freed/overran it, and where.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _6_MemoryBugsAndSanitizers.c && ./demo

# the buggy versions, under the sanitizers (each will abort with a report):
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo_s _6_MemoryBugsAndSanitizers.c
./demo_s --trigger     # watch the reports, then reread the code
```

## Why This Structure Exists
Every heap bug is a broken ownership rule — and the sanitizer is the fastest teacher of those rules ever built. Reading its reports fluently is the core skill the C++ lab formalized and this module drills.
