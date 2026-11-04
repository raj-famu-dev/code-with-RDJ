// Tags: #C #FileIO #BinaryIO #Endianness | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <string.h>
#include <stdint.h>

/* Binary I/O moves BYTES, not text — no '\n' translation, no formatting.
   fread/fwrite are memcpy-to/from-a-stream. */

typedef struct {
    uint32_t magic;        /* a file-format signature */
    uint32_t count;        /* how many records follow */
} FileHeader;

typedef struct {
    int32_t id;
    double value;
} Record;

/* Endianness check: does the first byte hold the LOW bits (little) or HIGH (big)? */
static int is_little_endian(void) {
    uint32_t x = 1;
    return *(unsigned char *)&x == 1;
}

int main(void) {
    printf("this machine is %s-endian\n", is_little_endian() ? "little" : "big");

    /* WRITE: header + records, as raw bytes */
    Record recs[2] = { { 101, 3.75 }, { 202, 3.50 } };
    FileHeader hdr = { 0x52444a00, 2 };      /* "RDJ\0" magic */

    FILE *f = fopen("_3_demo.bin", "wb");   /* b: binary mode */
    if (!f) { perror("fopen"); return 1; }
    fwrite(&hdr, sizeof hdr, 1, f);          /* &object, size, count, stream */
    fwrite(recs, sizeof recs[0], 2, f);     /* whole array in one call */
    fclose(f);

    /* READ it back and verify */
    FILE *in = fopen("_3_demo.bin", "rb");
    if (!in) { perror("fopen"); return 1; }

    FileHeader got = { 0 };
    if (fread(&got, sizeof got, 1, in) != 1) {   /* fread returns the ITEM count */
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
    printf("record 1: id=%d value=%.2f\n", back[1].id, back[1].value);

    /* THE PORTABILITY PROBLEM, stated:
       - struct padding (Module 03) can differ between compilers/platforms
       - endianness: this file's doubles are x86 byte order
       - sizeof(int)/alignments differ across ABIs
       Real wire/file formats fix all three: fixed-width types (stdint),
       explicit byte order, and memcpy-style field packing — no raw struct dumps. */
    printf("a raw struct dump is machine-dependent; real formats pack fields explicitly.\n");
    return 0;
}
