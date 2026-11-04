# `_5_Unions.c`

## Concept
A `union` stores all its members **in the same bytes** — an overlay. `sizeof` is the largest member; only the member last written is valid. It's the memory-saving trick behind tagged sum types, hardware registers, and type punning.

## The Code

```c
#include <stdio.h>
#include <string.h>
#include <stdint.h>

union raw64 {
    double d;
    uint64_t u;
    char bytes[8];
};

typedef struct {
    enum { SHAPE_CIRCLE, SHAPE_RECT } kind;
    union {
        struct { double radius; } circle;
        struct { double w, h; } rect;
    } as;
} Shape;

int main(void) {
    union raw64 r;
    r.d = 1.0;
    printf("as double: %.1f | as uint64: 0x%016llx | bytes: ", r.d, (unsigned long long)r.u);
    for (int i = 0; i < 8; i++) printf("%02x ", (unsigned char)r.bytes[i]);
    printf("\n(the IEEE-754 bit pattern of 1.0, little-endian)\n");

    printf("sizeof(union raw64) = %zu (largest member wins)\n", sizeof(union raw64));

    Shape s = { .kind = SHAPE_CIRCLE, .as.circle.radius = 2.0 };
    double area;
    if (s.kind == SHAPE_CIRCLE) {
        area = 3.14159265358979 * s.as.circle.radius * s.as.circle.radius;
    } else {
        area = s.as.rect.w * s.as.rect.h;
    }
    printf("circle area: %.3f\n", area);

    s.kind = SHAPE_RECT;
    s.as.rect.w = 3.0; s.as.rect.h = 4.0;
    printf("now a rect: %.1f x %.1f\n", s.as.rect.w, s.as.rect.h);
    return 0;
}
```

## Line-by-Line Breakdown

### `union raw64 { double d; uint64_t u; char bytes[8]; }`
Three views of the **same 8 bytes**. Write `d`, and `u` shows the IEEE-754 pattern; `bytes` shows them one at a time. `sizeof` is 8 — the largest member — not the sum (contrast with `struct`: same members would give 24).

### The overlay printout
`1.0` as a double is `0x3FF0000000000000` — the demo shows the actual bytes in memory order (little-endian on x86: `00 00 ... F0 3F`). This is exactly what a debugger shows you.

### The tagged union (`Shape`)
The pattern that powers every C interpreter/parser/database:
- `kind` — an enum saying **which** union member is valid
- `as` — the overlay holding the payload

Switch on the tag, then read the matching member. This is C's answer to Java's subclasses or C++'s `std::variant` — same idea, manual tag.

### `s.kind = SHAPE_RECT;` then writing `as.rect`
Switching the tag **invalidates the old payload** — `as.circle.radius`'s bytes are being reused by `w` now. Reading a member other than the last written is legal-but-meaningless (that's the trap, stated below).

## Traps
- **Reading the wrong member** is not a compile error and often not even a crash — you get garbage. The tag is the only truth; keep it correct.
- Writing one member and reading another (type punning) is formally UB in C outside `memcpy`/`char` views — GCC permits the union idiom, but compilers and the standard disagree; the safe route is `memcpy` between differently-typed objects.
- Forgetting to update the tag after writing a member — the classic tagged-union bug that `std::variant` (C++ lab, Module 05) exists to prevent.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _5_Unions.c && ./demo
```

## Why This Structure Exists
Hardware and protocols are unions in the wild: a register that is "an interrupt reason *or* a control word *or* four flags" depending on context. C's union models that exactly, at zero memory cost — and the tagged-union pattern extends it into a real sum type.
