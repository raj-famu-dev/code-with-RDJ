// Tags: #C #Structs #PassByValue #PassByPointer | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

typedef struct {
    double x, y, z;     /* 24 bytes — big enough to care about copying */
} Vec3;

/* BY VALUE: the whole struct is COPIED into the parameter.
   Fine for small structs; wasteful for big ones; required if you want a copy. */
Vec3 by_value(Vec3 v) {
    v.x = 99.0;                  /* modifies the COPY — caller sees nothing */
    return v;                    /* returning a struct also copies */
}

/* BY POINTER: one address (8 bytes) instead of the whole struct.
   The function can WRITE through it — this is C's out-parameter. */
void scale(Vec3 *v, double k) {
    v->x *= k;                   /* -> dereferences and accesses in one stroke */
    v->y *= k;
    v->z *= k;
}

/* BY CONST POINTER: pass cheaply, promise not to modify. The DEFAULT choice
   for any struct bigger than a word or two. */
double dot(const Vec3 *a, const Vec3 *b) {
    return a->x * b->x + a->y * b->y + a->z * b->z;
}

int main(void) {
    Vec3 v = { 1.0, 2.0, 3.0 };
    Vec3 w = { 4.0, 5.0, 6.0 };

    Vec3 modified = by_value(v);
    printf("by_value: caller's v.x is still %.1f (copy was changed)\n", v.x);
    printf("by_value returned the modified copy: x=%.1f\n", modified.x);

    scale(&v, 2.0);              /* pass the ADDRESS */
    printf("after scale(&v, 2): v = (%.1f, %.1f, %.1f)\n", v.x, v.y, v.z);

    printf("dot(v, w) = %.1f (read via const pointers)\n", dot(&v, &w));

    /* -> is pure sugar: v.x and (*v).x and pv->x are the same storage */
    Vec3 *pv = &v;
    printf("same storage: %.1f == %.1f == %.1f\n", (*pv).x, pv->x, v.x);

    /* sizeof comparison: the pointer is 8 bytes; the struct is 24 */
    printf("sizeof(Vec3)=%zu, sizeof(Vec3*)=%zu — passing by pointer moves 1/3 the bytes\n",
           sizeof(Vec3), sizeof(Vec3 *));
    return 0;
}
