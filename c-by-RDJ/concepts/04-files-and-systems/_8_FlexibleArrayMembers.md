# `_8_FlexibleArrayMembers.c`

## Concept
The **flexible array member**: a struct whose last field is an unsized array (`int items[]`). One `malloc` allocates the header *and* the payload together — the classic C idiom for variable-sized records, and the exact technique Module 05's dynamic array uses.

## The Code

```c
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>

typedef struct {
    size_t count;
    int items[];
} IntVec;

static IntVec *vec_new(size_t n) {
    size_t header = offsetof(IntVec, items);
    IntVec *v = malloc(header + n * sizeof(int));
    if (!v) return NULL;
    v->count = n;
    return v;
}

int main(void) {
    printf("sizeof(IntVec) = %zu (the flexible member adds NOTHING)\n", sizeof(IntVec));

    IntVec *v = vec_new(5);
    if (!v) return 1;
    for (size_t i = 0; i < v->count; i++) {
        v->items[i] = (int)(i * i);
    }
    printf("squares:");
    for (size_t i = 0; i < v->count; i++) printf(" %d", v->items[i]);
    printf("\n");

    IntVec *bigger = realloc(v, offsetof(IntVec, items) + 8 * sizeof(int));
    if (!bigger) { free(v); return 1; }
    v = bigger;
    v->count = 8;
    free(v);
    return 0;
}
```

## Line-by-Line Breakdown

### `int items[];`
The **flexible array member** (C99): an incomplete array that must be the **last member**. `sizeof(IntVec)` ignores it entirely — it's a marker for "the payload starts here", not storage.

### `offsetof(IntVec, items)` — the header size
The portable size of the header part: the offset where the payload begins. Using `sizeof(struct)` would *usually* work here but is not guaranteed (padding); `offsetof` is exact. **`malloc(offsetof(...) + n * sizeof(int))`** sizes the whole record.

### `v->items[i] = ...`
The payload sits immediately after the struct header in the same block — so plain indexing reaches it. One allocation, one cache-friendly contiguous layout, zero pointer chasing.

### `realloc` grows the whole record
The header and payload move *together* — the count is never separated from its items. Compare the two-alternative designs:
| Design | Allocations | Fragility |
|---|---|---|
| Flexible array member | **1** | one free; realloc moves all |
| struct with `int *items` | 2 | free both, in the right order; items can dangle |
| array of fixed `int items[64]` | 1 | hard cap, wasted space |

### The "struct hack" history
Before C99, code wrote `int items[1];` and over-allocated — the famous "struct hack", so common the standard eventually blessed the zero-size form.

## Traps
- `sizeof` of the struct is NOT the record's size — forgetting the `+ n * sizeof(int)` is an instant heap overflow (ASan catches it).
- A flexible member must be **last**; a struct with two flexible arrays is illegal.
- Copying the struct (`*v2 = *v`) copies only the header — the payload is not part of the struct. memcpy the whole block if you need a deep copy.
- Return-value discipline on `realloc` (Module 02): assign to a temporary, keep the original on failure.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _8_FlexibleArrayMembers.c && ./demo
# verify no leaks:
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo_s _8_FlexibleArrayMembers.c && ./demo_s
```

## Why This Structure Exists
This is the memory layout behind dynamic arrays (Module 05), variable-length network packets, and strings inside structs. One block, header + payload — C's answer to "an object whose size varies" without two allocations and a dangling risk.
