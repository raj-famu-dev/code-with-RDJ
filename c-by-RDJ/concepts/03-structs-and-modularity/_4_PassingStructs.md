# `_4_PassingStructs.c`

## Concept
How structs cross function boundaries: **by value** (copied — safe but costs bytes), **by pointer** (cheap, writable), and **by const pointer** (cheap, read-only — the default for anything non-tiny). Java hides this choice from you; C makes you make it, every time.

## The Code

```c
#include <stdio.h>

typedef struct {
    double x, y, z;
} Vec3;

Vec3 by_value(Vec3 v) {
    v.x = 99.0;
    return v;
}

void scale(Vec3 *v, double k) {
    v->x *= k;
    v->y *= k;
    v->z *= k;
}

double dot(const Vec3 *a, const Vec3 *b) {
    return a->x * b->x + a->y * b->y + a->z * b->z;
}

int main(void) {
    Vec3 v = { 1.0, 2.0, 3.0 };
    Vec3 w = { 4.0, 5.0, 6.0 };

    Vec3 modified = by_value(v);
    printf("by_value: caller's v.x is still %.1f (copy was changed)\n", v.x);
    printf("by_value returned the modified copy: x=%.1f\n", modified.x);

    scale(&v, 2.0);
    printf("after scale(&v, 2): v = (%.1f, %.1f, %.1f)\n", v.x, v.y, v.z);

    printf("dot(v, w) = %.1f (read via const pointers)\n", dot(&v, &w));

    Vec3 *pv = &v;
    printf("same storage: %.1f == %.1f == %.1f\n", (*pv).x, pv->x, v.x);

    printf("sizeof(Vec3)=%zu, sizeof(Vec3*)=%zu\n", sizeof(Vec3), sizeof(Vec3 *));
    return 0;
}
```

## Line-by-Line Breakdown

### `Vec3 by_value(Vec3 v)`
The argument is a **copy** of all 24 bytes. `v.x = 99.0` inside touches the copy; the caller is unaffected. Returning a struct copies it back. For small structs this is fine and pleasantly value-like — for a 10 KB struct it's a performance bug.

### `void scale(Vec3 *v, double k)`
The parameter is one pointer (8 bytes). `v->x` — the **arrow operator** — is `(*v).x` in one stroke: follow the address, then access the field. Writes through the pointer reach the caller's actual storage. This is how C functions "return" multiple results: pass pointers to where they should write.

### `double dot(const Vec3 *a, ...)`
The house style for struct parameters: **const pointer**. You get the by-value cost profile (8 bytes) with the borrow-only contract (`const` forbids `a->x = ...`). `printf`, every standard API, and your own code should default here.

### `(*pv).x == pv->x == v.x`
Three spellings, one storage. `->` exists purely because `(*p).field` is tedious. Note that `.` is for structs and `->` is for pointers — mixing them is a compile error, which saves you.

### The decision table
| Situation | Use |
|---|---|
| Small struct (a word or two), want a copy | by value |
| Function must modify the caller's struct | pointer |
| Bigger struct, read-only | `const T *` |
| Ownership transfer (heap object) | `T *` returned/stored, documented |

## Traps
- Returning a pointer to a **local** struct: the scope dies with the return — dangling pointer. Return by value, or take the memory from the heap (Module 02's ownership rules apply).
- Passing big structs by value in a hot loop: measure, then switch to `const T *`.
- `->` on a non-pointer (`v->x` where `v` is a `Vec3`) is a compile error; so is `.` on a pointer — the compiler has your back here.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _4_PassingStructs.c && ./demo
```

## Why This Structure Exists
C has exactly one parameter mechanism — copy — and the pointer is how you opt out of the cost or opt into mutation. Making that choice explicit per parameter is C's way of making the memory traffic of your program *visible*.
