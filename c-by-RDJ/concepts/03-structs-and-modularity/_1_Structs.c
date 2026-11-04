// Tags: #C #Structs | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <string.h>
#include <stddef.h>

/* A struct bundles related values of DIFFERENT types into one named unit.
   This is C's record — the closest thing to a Java class's fields (no methods). */
struct student {
    int id;
    char name[24];
    double gpa;
};

int main(void) {
    /* Three ways to initialize */
    struct student a = { 101, "RDJ", 3.75 };            /* positional */
    struct student b = { .id = 202, .gpa = 3.5 };      /* designated (C99): rest is zeroed */
    struct student c = a;                                /* copy: whole struct at once */

    /* Access with the dot operator */
    printf("a: %d %s %.2f\n", a.id, a.name, a.gpa);
    printf("b: %d %s %.2f (name zeroed by designated init)\n", b.id, b.name, b.gpa);
    printf("c: %d %s %.2f (a copy of a)\n", c.id, c.name, c.gpa);

    /* Assignment copies the WHOLE struct — unlike arrays! */
    c.gpa = 4.0;
    printf("after c.gpa=4.0, a.gpa is still %.2f (independent copies)\n", a.gpa);

    /* Strings inside structs are arrays: copy with strcpy, not = */
    strcpy(b.name, "Raj");
    printf("b.name now: %s\n", b.name);

    /* Padding: the compiler aligns fields for fast access, inserting holes. */
    printf("sizeof(struct student) = %zu\n", sizeof(struct student));
    printf("sum of members: %zu + %zu + %zu = %zu (the difference is padding)\n",
           sizeof(int), (size_t)24, sizeof(double),
           sizeof(int) + 24u + sizeof(double));
    printf("offsetof(name) = %zu, offsetof(gpa) = %zu\n",
           offsetof(struct student, name), offsetof(struct student, gpa));
    return 0;
}
