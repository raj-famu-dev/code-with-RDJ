# `_4_StringsAsCharPointers.c`

## Concept
"String" is spelled two ways in C and they mean different things: a `char` **array** (your storage, modifiable) vs a `char *` to a **literal** (read-only bytes). Confusing them is a classic undefined-behavior source.

## The Code

```c
#include <stdio.h>

int main(void) {
    char owned[] = "Hello";
    owned[0] = 'J';
    printf("owned: %s (own bytes, safe to modify)\n", owned);

    const char *lit = "Hello";
    printf("lit: %s (points at a read-only literal)\n", lit);

    printf("sizeof owned = %zu (the array), sizeof lit = %zu (the pointer)\n",
           sizeof owned, sizeof lit);

    const char *a = "same";
    const char *b = "same";
    printf("a == b? %s (deduplication is allowed, never assumed)\n", (a == b) ? "yes" : "no");

    size_t len = 0;
    while (owned[len] != '\0') {
        len++;
    }
    printf("hand-rolled strlen: %zu\n", len);
    return 0;
}
```

## Line-by-Line Breakdown

### `char owned[] = "Hello"`
The literal is **copied** into a 6-byte array on the stack. `owned` owns those bytes — modify freely. `sizeof owned` is 6 (the array).

### `const char *lit = "Hello"`
No copy. `lit` points at the literal itself — an anonymous array the compiler placed in read-only storage (often `.rodata`). `sizeof lit` is 8 (just a pointer). Writing `lit[0] = 'J'` is undefined behavior — a segfault on typical platforms. The `const` documents that contract.

### `a == b`
Two identical literals *may* be merged into one object — the compiler is allowed to deduplicate. Never rely on either outcome.

### The hand-rolled `strlen`
The loop `while (owned[len] != '\0') len++;` is what every `<string.h>` function does internally: walk until the terminator. One missing `'\0'` and the walk never stops.

### Ownership (preview of topics 5 and 8)
| Spelling | Storage | Who frees it |
|---|---|---|
| `char s[] = "x"` | stack (copied) | automatic — scope exit |
| `const char *p = "x"` | static, read-only | never (program lifetime) |
| `char *p = malloc(...)` | heap | **you** — `free(p)` |

## Traps
- `char *p = "x"; p[0] = 'y';` — compiles (with warnings at best), crashes or worse.
- `owned` (array) assigned to a `char *` decays fine — but the pointer outlives the array at its peril (dangling pointer, Module 08 of the C++ lab's twin lesson).
- String literals' type is `char[N]` in C (no `const` in the type!) for historical reasons — compilers warn when you point a plain `char *` at one; take the warning seriously.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _4_StringsAsCharPointers.c && ./demo
```

## Why This Structure Exists
Arrays give you ownership and cost a copy; pointers to literals give you zero-cost constants at the price of immutability. Choosing deliberately between them is the first "ownership decision" C makes you practice.
