# `_1_Structs.c`

## Concept
`struct` — C's record type: named fields of different types in one unit. It's the "fields, no methods" ancestor of the Java class, and the base type of almost every real C API.

## The Code

```c
#include <stdio.h>
#include <string.h>
#include <stddef.h>

struct student {
    int id;
    char name[24];
    double gpa;
};

int main(void) {
    struct student a = { 101, "RDJ", 3.75 };
    struct student b = { .id = 202, .gpa = 3.5 };
    struct student c = a;

    printf("a: %d %s %.2f\n", a.id, a.name, a.gpa);
    printf("b: %d %s %.2f (name zeroed by designated init)\n", b.id, b.name, b.gpa);
    printf("c: %d %s %.2f (a copy of a)\n", c.id, c.name, c.gpa);

    c.gpa = 4.0;
    printf("after c.gpa=4.0, a.gpa is still %.2f (independent copies)\n", a.gpa);

    strcpy(b.name, "Raj");
    printf("b.name now: %s\n", b.name);

    printf("sizeof(struct student) = %zu\n", sizeof(struct student));
    printf("offsetof(name) = %zu, offsetof(gpa) = %zu\n",
           offsetof(struct student, name), offsetof(struct student, gpa));
    return 0;
}
```

## Line-by-Line Breakdown

### `struct student { ... };`
Defines a **type**, allocates nothing. Fields are laid out in declaration order. The name `struct student` is the full type name — hence `typedef` (next topic).

### Positional init `{ 101, "RDJ", 3.75 }`
Fields in order. The string literal is copied into the array member — safe.

### Designated init `{ .id = 202, .gpa = 3.5 }` (C99)
Set by name; **every unmentioned member is zeroed**. The best default for config-like structs: `struct options o = {0};` zeroes everything.

### `struct student c = a;` — whole-struct copy
Unlike arrays (which decay), a struct assigned by value copies **all its bytes**. `c.gpa = 4.0` doesn't touch `a`. This rule makes structs feel "object-like" — but members that are pointers copy the address, not the target (shallow copy — the trap of every language).

### `strcpy(b.name, "Raj")`
The `name` member is an array inside the struct — assignment (`b.name = ...`) is illegal; it's the string rules from Module 01 applied inside a record.

### Padding and `offsetof`
CPUs like aligned accesses, so the compiler inserts invisible holes: `int` (4) + `char[24]` (24) + `double` (8) = 36, but the struct is **40** — the compiler padded so `gpa` sits at an 8-aligned offset. `offsetof` (from `<stddef.h>`) shows each field's real offset. This matters the moment you write structs to files or the network (Module 04) or index them by hand.

## Traps
- Padding makes `sizeof` bigger than the member sum — never compute struct sizes by hand; always `sizeof`.
- Comparing structs with `==` is illegal — compare member by member (or `memcmp`, carefully, padding included).
- A struct containing a pointer: the copy shares the pointee.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _1_Structs.c && ./demo
```

## Why This Structure Exists
Records are the shape of real data. C gives them to you with zero runtime machinery: plain bytes, a layout you can inspect (`offsetof`), and value semantics you can rely on.
