# `_3_NestedAndArrayOfStructs.c`

## Concept
Composition in C: structs inside structs, and arrays of structs — the two layouts that make C good at modeling records. Plus the nested-access syntax and the contiguous-memory picture that makes it fast.

## The Code

```c
#include <stdio.h>

typedef struct {
    int year, month, day;
} Date;

typedef struct {
    char title[40];
    Date published;
    double price;
} Book;

int main(void) {
    Book shelf[3] = {
        { "The C Programming Language", { 1988, 3, 22 }, 45.0 },
        { "Modern C",                   { 2019, 6, 10 }, 30.0 },
        { "Pointers on C",              { 1997, 8, 4 },  55.0 }
    };

    size_t n = sizeof shelf / sizeof shelf[0];

    printf("%s (%d) costs $%.2f\n", shelf[0].title, shelf[0].published.year, shelf[0].price);

    double total = 0;
    for (size_t i = 0; i < n; i++) {
        total += shelf[i].price;
    }
    printf("total value: $%.2f\n", total);

    Book gift = shelf[1];
    gift.price = 0.0;
    printf("gift is a copy: shelf[1] still $%.2f\n", shelf[1].price);

    for (size_t i = 0; i < n; i++) {
        size_t best = i;
        for (size_t j = i + 1; j < n; j++)
            if (shelf[j].published.year < shelf[best].published.year) best = j;
        if (best != i) { Book tmp = shelf[i]; shelf[i] = shelf[best]; shelf[best] = tmp; }
    }
    return 0;
}
```

## Line-by-Line Breakdown

### `Book shelf[3]`
An array of structs: `3 * sizeof(Book)` contiguous bytes. This is the layout of every table-like C program — and of `std::vector<Book>` under the hood in the C++ lab.

### Nested initializer `{ ..., { 1988, 3, 22 }, ... }`
Braces nest to match the struct: the inner `{ }` initializes `Date published`. (Omit them and a flattened list also works, but nested is readable.)

### `shelf[0].published.year`
Access chains left to right: index the array, then dot into the struct, then dot into the nested struct.

### `Book gift = shelf[1];`
Whole-element copy — the value semantics from `_1_Structs`, now per array element. `gift.price = 0` does not discount the shelf.

### The selection sort
The classic pattern for sorting an array of structs **by hand**: find the best element, swap whole structs (a `Book tmp` — whole-struct assignment makes the swap trivial). Module 05's `_5_Sorting` replaces the hand-roll with `qsort`; `qsort` swaps bytes instead, which changes the picture.

### The memory picture
`sizeof(Book)` bytes per element, no pointers anywhere — everything inline. Cache-friendly (one memory sweep walks the whole shelf), and `offsetof` from `_1_Structs` tells you exactly where each field of each element sits.

## Traps
- Inserting into the middle of an array of structs moves whole records — O(n) copies. If that's hot, an array of *pointers* to structs trades locality for cheap moves (the C++ lab's `list` vs `vector` tradeoff, in C).
- Nested initializers and designated initializers combine: `{ .published.year = 2020 }` — legal but noisy; prefer full nested braces.
- A struct can contain an **array**, but an array of structs containing pointers to *themselves* (trees, lists) needs the tag + pointer pattern from `_2_Typedef`.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _3_NestedAndArrayOfStructs.c && ./demo
```

## Why This Structure Exists
"Array of structs" is C's table; "struct of arrays" is its columnar twin (used when only one field is hot). Choosing between them — and between inline data and pointers — is C's core data-layout skill.
