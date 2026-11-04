// Tags: #C #Typedef #Structs | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

/* Without typedef, the type's full name is 'struct student'. */
struct student_v1 {
    int id;
    double gpa;
};

/* With typedef, the struct gets a one-word alias.
   Pattern: define the struct, then typedef it. */
typedef struct student_v2 {
    int id;
    double gpa;
} Student;

/* The anonymous-struct pattern: no tag needed at all. */
typedef struct {
    double x, y;
} Point;

/* Typedefs are for READABILITY of existing types too. */
typedef unsigned char byte;
typedef struct student_v2 StudentAlias;   /* an alias of an alias */

int main(void) {
    struct student_v1 old_way = { 1, 3.0 };   /* must spell 'struct' */
    Student new_way = { 2, 3.5 };               /* one word */
    Point p = { 1.5, 2.5 };
    byte b = 255;

    printf("old: %d %.1f | new: %d %.1f\n", old_way.id, old_way.gpa, new_way.id, new_way.gpa);
    printf("point: (%.1f, %.1f), byte: %u\n", p.x, p.y, b);

    /* The SAME type, three spellings — typedef creates aliases, not new types. */
    StudentAlias same = new_way;
    same.gpa = 4.0;
    printf("the alias is the same type; the copy is independent: %.1f vs original %.1f\n",
           same.gpa, new_way.gpa);
    return 0;
}
