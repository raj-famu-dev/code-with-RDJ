# `_6_EnumsAndBitfields.c`

## Concept
Enums are named integer constants (the tag for tagged unions, the cases for `switch`). Bitfields are struct members measured in **bits** — how C models hardware registers and flag sets. Together with the OR-masks idiom, they are C's whole vocabulary of "small named numbers".

## The Code

```c
#include <stdio.h>

enum status { OK = 0, ERR_IO = 1, ERR_NET = 2, ERR_FATAL = 3 };
enum color { RED, GREEN, BLUE };

typedef struct {
    unsigned int enabled   : 1;
    unsigned int mode      : 2;
    unsigned int priority  : 3;
    unsigned int           : 2;
    unsigned int reserved  : 4;
} Reg32;

int main(void) {
    enum status s = ERR_NET;
    printf("status = %d\n", s);
    s = (s == ERR_NET) ? OK : ERR_FATAL;

    switch (s) {
    case OK:       printf("all good\n"); break;
    case ERR_IO:   printf("io problem\n"); break;
    case ERR_NET:  printf("net problem\n"); break;
    case ERR_FATAL: printf("fatal\n"); break;
    }

    Reg32 r = { 0 };
    r.enabled = 1;
    r.mode = 3;
    r.priority = 5;
    printf("enabled=%u mode=%u priority=%u\n", r.enabled, r.mode, r.priority);
    printf("sizeof(Reg32) = %zu\n", sizeof(Reg32));

    r.priority = 9;
    printf("priority=9 stored as %u (truncated!)\n", r.priority);

    enum { CAP_READ = 1, CAP_WRITE = 2, CAP_EXEC = 4 };
    unsigned caps = CAP_READ | CAP_EXEC;
    printf("caps: read=%d write=%d exec=%d\n",
           (caps & CAP_READ) != 0, (caps & CAP_WRITE) != 0, (caps & CAP_EXEC) != 0);
    return 0;
}
```

## Line-by-Line Breakdown

### `enum status { OK = 0, ... }`
Explicit values. Without them (`enum color`), values auto-increment from 0. **An enum constant is an `int`** — you can print it, compare it, and (unlike Java) assign an out-of-range value to an enum variable with only a compiler grumble. Enums are documentation, not type safety.

### `switch` on an enum
The natural pairing — the compiler warns about unhandled cases (with `-Wswitch`) only when switching on an enum type, which is why enums + switch is the standard C idiom.

### `unsigned int enabled : 1;`
A bitfield: name, underlying type, colon, **width in bits**. `mode : 2` holds 0–3; `priority : 3` holds 0–7. The compiler packs them into one storage unit — `sizeof(Reg32)` is 4 bytes, not 12 × 4. The unnamed `: 2` is deliberate padding (alignment with a real register layout).

### `r.priority = 9` → stored as `1`
**Bitfields truncate silently**: 9 is `1001` binary; only the low 3 bits (`001`) fit. No error, no warning. This is the trap that makes you double-check widths against the hardware datasheet.

### `CAP_READ = 1, CAP_WRITE = 2, CAP_EXEC = 4`
The powers-of-two enum: one bit per capability. `|` combines them into a mask; `&` tests one; the demo's `(caps & CAP_READ) != 0` pattern is the portable truth-test (never compare `&` to nonzero as a boolean — style and correctness).

## Traps
- Bitfield layout (order, padding, crossing storage units) is **implementation-defined** — never write bitfield structs to disk or the network expecting bit-exact portability. Use explicit shifts and masks for wire formats.
- Enum values are ints — passing `42` where an `enum status` is expected compiles.
- `sizeof` of an enum is `sizeof(int)` typically — enums save *readability*, not memory (unlike bitfields).

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _6_EnumsAndBitfields.c && ./demo
```

## Why This Structure Exists
Between "one named constant" and "one integer" lies a whole spectrum of intent: enum for exclusive alternatives, bitfield for packed hardware-shaped data, OR-masks for independent flags. C gives you all three because its users write all three kinds of code.
