# `_2_VariablesAndTypes.c`

## Concept
C is statically typed with a small set of built-in types — and unlike Java, their exact sizes are the machine's choice. The fix is the fixed-width types from `<stdint.h>`, which is what real systems code uses.

## The Code

```c
#include <stdio.h>
#include <stdint.h>
#include <limits.h>
#include <stdbool.h>

int main(void) {
    int    a = 42;
    long   big = 9000000000L;
    double d = 3.14;
    char   c = 'A';
    bool   flag = true;
    unsigned u = 4000000000u;

    int32_t exact32 = 2147483647;
    int64_t exact64 = 9000000000000000000LL;
    uint8_t one_byte = 255;

    printf("int=%d long=%ld double=%.2f char=%c bool=%d unsigned=%u\n",
           a, big, d, c, flag, u);
    printf("int32=%d int64=%lld uint8=%u\n", exact32, (long long)exact64, one_byte);
    printf("INT_MAX=%d INT_MIN=%d UINT_MAX=%u\n", INT_MAX, INT_MIN, UINT_MAX);
    printf("CHAR_BIT=%d (a byte has %d bits on this machine)\n", CHAR_BIT, CHAR_BIT);
    return 0;
}
```

## Line-by-Line Breakdown

### The basic types
| Type | Meaning | Typical size (this machine) |
|---|---|---|
| `char` | one byte; character code | 1 byte |
| `short` | small integer | 2 bytes |
| `int` | default integer | 4 bytes |
| `long` | larger integer | 8 bytes |
| `float` / `double` | floating point | 4 / 8 bytes |
| `bool` | true/false (needs `<stdbool.h>`) | 1 byte |

The C standard only guarantees minimum sizes and an ordering — the machine decides. Java's `int` is *always* 32 bits; C's `int` is "at least 16".

### `unsigned u`
Drops the sign bit — the range shifts: no negatives, double the positive maximum. Wraparound is *defined* for unsigned types (this becomes a real tool in Module 02).

### Fixed-width types (`<stdint.h>`)
| Type | Guaranteed size |
|---|---|
| `int8_t` / `uint8_t` | exactly 8 bits |
| `int32_t` / `uint32_t` | exactly 32 bits |
| `int64_t` / `uint64_t` | exactly 64 bits |

`exact32` behaves identically on every platform — that's why file formats, protocols and kernels use them.

### `<limits.h>`
Publishes the platform's ranges: `INT_MAX`, `INT_MIN`, `UINT_MAX`, `CHAR_BIT`. Java has `Integer.MAX_VALUE` as a constant; C has it as a header.

### Format specifiers
`%d` (int), `%ld` (long), `%lld` (long long), `%u` (unsigned), `%f`/`%.2f` (double), `%c` (char), `%zu` (size_t). A mismatch between a specifier and its argument is **undefined behavior** — the compiler usually can't catch it.

## Traps
- `char`'s signedness is implementation-defined — use `int8_t`/`uint8_t` when it matters.
- C has no `String` type — strings arrive in Module 01 topic 7.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _2_VariablesAndTypes.c && ./demo
```

## Why This Structure Exists
C began as a systems language: types map to what the hardware offers, and `<stdint.h>` adds the portability layer when the hardware's choice isn't good enough.
