# `_1_PointersAndAddresses.c`

## Concept
A pointer is a variable whose value is a **memory address**. `&` takes an address, `*` follows one. Everything distinctive about C — arrays, strings, heap memory, data structures — is built on this one idea.

## The Code

```c
#include <stdio.h>

int main(void) {
    int x = 42;

    int *p = &x;

    printf("x lives at %p and holds %d\n", (void *)&x, x);
    printf("p holds %p and points at %d\n", (void *)p, *p);

    *p = 99;
    printf("after *p = 99, x = %d (same storage, reached via p)\n", x);

    printf("sizeof(int*)=%zu sizeof(double*)=%zu sizeof(void*)=%zu\n",
           sizeof(int *), sizeof(double *), sizeof(void *));

    int *q = NULL;
    if (q == NULL) {
        printf("q is NULL — check before you dereference\n");
    }

    int **pp = &p;
    printf("**pp = %d (follow twice to reach x)\n", **pp);
    return 0;
}
```

## Line-by-Line Breakdown

### `int *p = &x;`
Two operators meet: `&x` produces x's address; `int *` declares that `p` stores an address of an `int`. Read it right-to-left: "p is a pointer to int."

### `*p` — the dereference
`*` follows the address to the storage itself. Reading `*p` reads `x`; writing `*p = 99` writes `x`. One storage, two names — this is how C functions "return" multiple values (Module 01's `swap_works`).

### `%p`
The pointer-format specifier; cast to `(void *)` for portability. Addresses are usually printed only while learning or debugging.

### `sizeof(int *) == sizeof(double *)`
A pointer is just an address: 8 bytes on 64-bit machines, no matter the pointee. The *type* of the pointer tells the compiler what to expect at the far end — it affects dereference size, not pointer size.

### `NULL`
A special address meaning "no object". Dereferencing it crashes (segmentation fault; ASan reports it precisely). The rule: **check for NULL before dereferencing** when a pointer might not be set.

### `int **pp = &p`
A pointer to a pointer: follow twice (`**pp`) to reach `x`. `argv` in Module 04 is exactly this shape (`char **`).

## Traps
- Uninitialized (garbage) pointers are worse than NULL — they point at random memory. Initialize everything.
- `int* a, b;` — only `a` is a pointer; `b` is a plain `int`. The asterisk binds to the name.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _1_PointersAndAddresses.c && ./demo
```

## Why This Structure Exists
Memory is one long numbered array of bytes; a pointer is just a number that indexes it. C exposes that directly because its job is to control memory precisely — and everything else (arrays, strings, `malloc`, structs-by-pointer) is this idea applied.
