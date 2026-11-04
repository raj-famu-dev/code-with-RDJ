# `_5_StackVsHeap.c`

## Concept
Two kinds of memory: the **stack** (automatic, scoped, freed for you) and the **heap** (requested with `malloc`, freed by *you* with `free`). This is the allocation discipline Java's GC does for you — the single skill that defines C programming.

## The Code

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int on_stack[100];
    on_stack[0] = 1;
    printf("stack: 100 ints, %zu bytes, freed automatically at scope exit\n",
           sizeof on_stack);

    int *on_heap = malloc(100 * sizeof *on_heap);
    if (on_heap == NULL) {
        fprintf(stderr, "allocation failed\n");
        return 1;
    }
    on_heap[0] = 2;
    printf("heap: 100 ints at %p, alive until free()\n", (void *)on_heap);

    int *zeroed = calloc(100, sizeof *zeroed);
    if (zeroed) {
        printf("calloc: first element is %d (zeroed)\n", zeroed[0]);
        free(zeroed);
    }

    int *grown = realloc(on_heap, 200 * sizeof *grown);
    if (grown == NULL) {
        free(on_heap);
        fprintf(stderr, "realloc failed\n");
        return 1;
    }
    on_heap = grown;

    free(on_heap);
    on_heap = NULL;
    return 0;
}
```

## Line-by-Line Breakdown

### The stack: `int on_stack[100]`
Allocated by entering the scope, released by leaving it — a single stack-pointer adjustment. No failure mode, no leak possible, but it dies with the scope and the total is small (MBs).

### `malloc(100 * sizeof *on_heap)`
Requests 400 bytes from the heap. Returns `void *` (implicitly converted), or **NULL on failure** — always check. Note `sizeof *on_heap`: sizeof of the *dereferenced pointer* — the idiom that keeps the expression correct even if the type changes.

### `calloc(100, sizeof *zeroed)`
`malloc` + zeroed. Use it when the memory must start clean.

### `realloc(on_heap, 200 * ...)`
Grows (or shrinks) a block, preserving contents. It may return a **different address** (it can move the block). On failure it returns NULL and leaves the *original* valid — so assign to a temporary, not straight to `on_heap`, or you lose the original pointer.

### `free(on_heap); on_heap = NULL;`
The discipline: free exactly once, then NULL the pointer. `free(NULL)` is a defined no-op — so a stray double-free of a NULLed pointer is harmless. A double-free of a live pointer is undefined behavior (glibc aborts; ASan reports it precisely).

### The leak
Every `malloc` without a matching `free` on *every* exit path leaks. Small programs survive; long-running servers die. LeakSanitizer (part of ASan) reports them at exit.

## Traps
- `free(stack_array)` — freeing a stack address: UB. `free` is only for heap pointers.
- Using the pointer after `free` — use-after-free, the next topic's star.
- `int *p = malloc(...); if (p == NULL) return;` then later code assumes `p` is valid — one error path skips the work, not the cleanup.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _5_StackVsHeap.c && ./demo
# and under the sanitizers:
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo_s _5_StackVsHeap.c && ./demo_s
```

## Why This Structure Exists
The stack gives you speed and automatic cleanup for scoped data; the heap gives you lifetime control for data that outlives scopes. C makes you choose, explicitly, for every allocation — which is exactly what Module 08's ownership patterns formalize.
