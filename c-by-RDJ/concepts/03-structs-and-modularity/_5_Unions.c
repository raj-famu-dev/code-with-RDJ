// Tags: #C #Unions #TypePunning | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <string.h>
#include <stdint.h>

/* A union overlays ALL members on the SAME bytes. sizeof = the largest member.
   Only ONE member is valid at a time — the last one written. */
union raw64 {
    double d;
    uint64_t u;
    char bytes[8];
};

/* The TAGGED UNION: the classic C sum type. A separate 'tag' field says
   which member is valid. This is how C does "one of several types". */
typedef struct {
    enum { SHAPE_CIRCLE, SHAPE_RECT } kind;   /* the tag */
    union {
        struct { double radius; } circle;
        struct { double w, h; } rect;
    } as;                                       /* the payload */
} Shape;

int main(void) {
    /* The overlay: write one member, read the same bytes through another */
    union raw64 r;
    r.d = 1.0;
    printf("as double: %.1f | as uint64: 0x%016llx | bytes: ", r.d, (unsigned long long)r.u);
    for (int i = 0; i < 8; i++) printf("%02x ", (unsigned char)r.bytes[i]);
    printf("\n(the IEEE-754 bit pattern of 1.0, little-endian)\n");

    /* sizeof is the largest member — all three views share the same 8 bytes */
    printf("sizeof(union raw64) = %zu (largest member wins)\n", sizeof(union raw64));

    /* THE TAGGED UNION in use */
    Shape s = { .kind = SHAPE_CIRCLE, .as.circle.radius = 2.0 };
    double area;
    if (s.kind == SHAPE_CIRCLE) {
        area = 3.14159265358979 * s.as.circle.radius * s.as.circle.radius;
    } else {
        area = s.as.rect.w * s.as.rect.h;
    }
    printf("circle area: %.3f\n", area);

    /* Switch the tag, then write the OTHER member — the old one is now garbage */
    s.kind = SHAPE_RECT;
    s.as.rect.w = 3.0; s.as.rect.h = 4.0;
    printf("now a rect: %.1f x %.1f, area %.1f\n", s.as.rect.w, s.as.rect.h,
           s.as.rect.w * s.as.rect.h);

    /* Reading the WRONG member is the trap this file exists to show:
       reading r.d after writing r.u is meaningless-but-legal. */
    return 0;
}
