# `_3_BinaryIO.c`

## Concept
`fread`/`fwrite` move raw bytes — structs, arrays, numbers — with no text formatting. The catch: raw bytes are only meaningful on a machine shaped like yours (padding, endianness, sizes). Real file formats pin all three down.

## The Code

```c
#include <stdio.h>
#include <stdint.h>

typedef struct {
    uint32_t magic;
    uint32_t count;
} FileHeader;

typedef struct {
    int32_t id;
    double value;
} Record;

static int is_little_endian(void) {
    uint32_t x = 1;
    return *(unsigned char *)&x == 1;
}

int main(void) {
    printf("this machine is %s-endian\n", is_little_endian() ? "little" : "big");

    Record recs[2] = { { 101, 3.75 }, { 202, 3.50 } };
    FileHeader hdr = { 0x52444a00, 2 };

    FILE *f = fopen("_3_demo.bin", "wb");
    if (!f) { perror("fopen"); return 1; }
    fwrite(&hdr, sizeof hdr, 1, f);
    fwrite(recs, sizeof recs[0], 2, f);
    fclose(f);

    FILE *in = fopen("_3_demo.bin", "rb");
    if (!in) { perror("fopen"); return 1; }

    FileHeader got = { 0 };
    if (fread(&got, sizeof got, 1, in) != 1) {
        fprintf(stderr, "short read on header\n");
        fclose(in);
        return 1;
    }
    if (got.magic != hdr.magic) {
        fprintf(stderr, "bad magic: this is not our file\n");
        fclose(in);
        return 1;
    }
    printf("magic OK, count = %u records\n", got.count);

    Record back[2] = { 0 };
    if (fread(back, sizeof back[0], (size_t)got.count, in) != got.count) {
        fprintf(stderr, "short read on records\n");
        fclose(in);
        return 1;
    }
    fclose(in);

    printf("record 0: id=%d value=%.2f (round-trip intact)\n", back[0].id, back[0].value);
    return 0;
}
```

## Line-by-Line Breakdown

### `fwrite(&hdr, sizeof hdr, 1, f)`
Four arguments: source pointer, **item size**, **item count**, stream. It writes `size * count` raw bytes — no format, no newline translation (that's the `b` mode's job on systems where it matters). Returns the count of **items** written — check it.

### `fread(...)` returns the item count too
A short count means EOF or error hit mid-item — the demo treats it as failure and bails. Reading is where validation lives.

### The **magic number** pattern
`0x52444a00` ("RDJ\0") at the head of the file: if it doesn't match, this isn't our format — fail fast instead of parsing garbage. Every real format has one (PNG's is `89 50 4E 47`).

### `is_little_endian()`
Store 1 as a 4-byte int; if the *first* byte in memory is 1, the low byte came first — little-endian. The demo prints the answer because the file's meaning depends on it: on a big-endian machine, those `uint32_t`s read back wrong without conversion.

### The portability problem (stated in the code)
A raw struct dump bakes in three machine assumptions:
1. **Padding** — where the compiler put the holes (Module 03's `offsetof` demo)
2. **Endianness** — byte order within each multi-byte number
3. **Sizes/alignment** — across compilers and ABIs

Real formats fix all three: fixed-width types (`stdint.h`), a declared byte order (usually big-endian "network order"), and field-by-field packing — which is exactly what the networking lab's `struct.pack` does in Python.

## Traps
- `fwrite(recs, sizeof recs, ...)` vs `sizeof recs[0]` — size/count ambiguity is a classic bug; be consistent (size = one item, count = items).
- `fread` into a too-small buffer overflows — the count is *your* responsibility.
- Comparing read-back structs with `==` is illegal (and padding is uninitialized garbage).

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _3_BinaryIO.c && ./demo
xxd _3_demo.bin | head -3    # see the raw bytes: magic, count, then records
```

## Why This Structure Exists
Binary is the native speed of I/O — no formatting, no parsing, just bytes. The magic-number + count + records layout here is the skeleton of every binary format from PNG to ELF executables.
