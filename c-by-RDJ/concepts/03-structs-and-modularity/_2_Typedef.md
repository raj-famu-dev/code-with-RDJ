# `_2_Typedef.c`

## Concept
`typedef` gives a type a new name. For structs it removes the mandatory `struct` keyword; for scalar types it documents intent. It creates an **alias**, not a new type — nothing is wrapped, nothing is checked.

## The Code

```c
#include <stdio.h>

struct student_v1 {
    int id;
    double gpa;
};

typedef struct student_v2 {
    int id;
    double gpa;
} Student;

typedef struct {
    double x, y;
} Point;

typedef unsigned char byte;
typedef struct student_v2 StudentAlias;

int main(void) {
    struct student_v1 old_way = { 1, 3.0 };
    Student new_way = { 2, 3.5 };
    Point p = { 1.5, 2.5 };
    byte b = 255;

    printf("old: %d %.1f | new: %d %.1f\n", old_way.id, old_way.gpa, new_way.id, new_way.gpa);
    printf("point: (%.1f, %.1f), byte: %u\n", p.x, p.y, b);

    StudentAlias same = new_way;
    same.gpa = 4.0;
    printf("alias writes through to the same struct: %.1f\n", new_way.gpa);
    return 0;
}
```

## Line-by-Line Breakdown

### `struct student_v1` — no typedef
Every declaration must spell `struct student_v1`. C purists note the tag *is* the type's name; `typedef` is sugar.

### `typedef struct student_v2 { ... } Student;`
Two things in one statement: defines the struct and aliases it to `Student`. Now `Student s;` works. This is the most common spelling in real code.

### Anonymous `typedef struct { ... } Point;`
No tag at all — fine when the struct will never be named again. If it needs to contain a pointer to *itself* (a linked-list node), the tag is required.

### `typedef unsigned char byte;`
Typedefs shine for intent: `byte`, `meters`, `timestamp_t`. But they are aliases — `byte` and `unsigned char` are interchangeable to the compiler, with no type safety between two aliases of the same underlying type.

### `StudentAlias same = new_way;`
Same type under another name; assignment is a normal struct copy. (The demo's print makes the point that the *copy* is independent — the alias changes nothing about semantics.)

## Traps
- Typedef'd pointers hide pointer-ness: `typedef char *string_t;` then `string_t a, b;` gives **two** pointers (the `*` binding surprise from Module 02 again) — and readers can't see that `string_t` is a pointer at the call site. Prefer visible `char *`.
- `typedef struct A B;` before `struct A` is complete is the forward-declaration idiom for opaque types (the "private class" of C — Module 08 uses it).
- In headers, typedef the struct *and* the struct tag together so both spellings work across files.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _2_Typedef.c && ./demo
```

## Why This Structure Exists
C's type names are built from English phrases (`struct student_v1 *`, `int (*)(int, char**)`) that grow unwieldy — `typedef` is the language's mechanism for giving them pronounceable names, and nearly every real API uses one for its main handle types.
