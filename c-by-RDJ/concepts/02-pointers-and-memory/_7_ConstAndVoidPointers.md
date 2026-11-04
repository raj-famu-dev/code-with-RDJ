# `_7_ConstAndVoidPointers.c`

## Concept
`const` documents who may write what, and `void *` is the "type-free" pointer that lets generic interfaces (`malloc`, `memcpy`, `qsort`) work with any data. Both are contracts — read them right-to-left.

## The Code

```c
#include <stdio.h>
#include <stdlib.h>

void print_ints(const int *data, size_t n) {
    for (size_t i = 0; i < n; i++) printf("%d ", data[i]);
    printf("\n");
}

void fixed_view(int *const p) {
    *p = 5;
    printf("int *const: can write *p (%d), cannot move p\n", *p);
}

int main(void) {
    int a[3] = { 1, 2, 3 };
    print_ints(a, 3);

    int x = 1;
    fixed_view(&x);

    void *v = a;
    int *back = v;
    printf("cast back: %d %d\n", back[0], back[1]);

    double *d = malloc(4 * sizeof *d);
    if (!d) return 1;
    d[0] = 2.5;
    printf("malloc's void* became double*: %.1f\n", d[0]);
    free(d);

    const int *p1;
    int *const p2 = &x;
    const int *const p3 = &x;
    return 0;
}
```

## Line-by-Line Breakdown

### The const ladder (read right to left)
| Declaration | Read as | You may |
|---|---|---|
| `const int *p` | p is a pointer to const int | move `p`, not write `*p` |
| `int *const p` | p is a const pointer to int | write `*p`, not move `p` |
| `const int *const p` | const pointer to const int | neither |

`const` binds to what is on its **left**; if nothing is on its left (leading `const`), it binds right. This is the one reading rule that makes every C declaration decodable.

### `void print_ints(const int *data, ...)`
Read-only array parameter: the compiler rejects `data[0] = 9` inside the function. Passing a plain `int *` is fine — you're widening the promise, never breaking it.

### `void *v = a;`
`void *` holds any object's address. It's what makes C generic: `malloc`, `memcpy`, `memset`, `qsort` all traffic in `void *`. But the compiler knows **nothing** about the far end:
- You cannot dereference (`*v` — of what type?)
- You cannot do arithmetic (`v + 1` — of what size?)

So a `void *` is a **shipment box**, not a usable pointer: you must cast it back to its real type (something only *you* know) before use.

### `int *back = v;`
In C, `void *` converts to and from any object pointer implicitly (no cast needed — but writing the cast is fine documentation).

### `malloc` returns `void *`
That's why `int *p = malloc(n * sizeof *p)` needs no cast in C (C++ requires one — a real difference between the languages).

## Traps
- Casting a `void *` to the **wrong** type compiles and is UB — the box doesn't remember what's inside.
- `const int *p` still allows `p` to alias data someone *else* can write — const is a promise by *this* pointer, not a property of the data.
- `void *` from `malloc` + wrong arithmetic after a bad cast = heap corruption; sanitizers catch it.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _7_ConstAndVoidPointers.c && ./demo
```

## Why This Structure Exists
`const` is C's lightweight contract — it costs nothing at runtime and documents intent where the compiler can enforce it. `void *` is C's generics: one mechanism (type-erased pointers) behind `malloc`, `memcpy`, `qsort`, and every callback API in the standard library.
