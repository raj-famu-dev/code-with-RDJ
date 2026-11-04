// Tags: #C #Structs #NestedStructs | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>

typedef struct {
    int year, month, day;
} Date;

typedef struct {
    char title[40];
    Date published;        /* a struct inside a struct */
    double price;
} Book;

int main(void) {
    /* Array of structs: the workhorse data layout of C. */
    Book shelf[3] = {
        { "The C Programming Language", { 1988, 3, 22 }, 45.0 },
        { "Modern C",                   { 2019, 6, 10 }, 30.0 },
        { "Pointers on C",              { 1997, 8, 4 },  55.0 }
    };

    size_t n = sizeof shelf / sizeof shelf[0];
    printf("shelf holds %zu books\n", n);

    /* Nested access chains the dots */
    printf("%s (%d) costs $%.2f\n", shelf[0].title, shelf[0].published.year, shelf[0].price);

    /* Walk the array of structs */
    double total = 0;
    for (size_t i = 0; i < n; i++) {
        total += shelf[i].price;
    }
    printf("total value: $%.2f\n", total);

    /* The memory picture: one contiguous block, sizeof(Book) per element */
    printf("sizeof(Book) = %zu; 3 * that = %zu = sizeof shelf\n",
           sizeof(Book), 3 * sizeof(Book));

    /* Copy one element: whole-struct assignment */
    Book gift = shelf[1];
    gift.price = 0.0;
    printf("gift is a copy: $%.2f, shelf[1] still $%.2f\n", gift.price, shelf[1].price);

    /* Sort by year using a scratch copy (hand-rolled selection sort) */
    for (size_t i = 0; i < n; i++) {
        size_t best = i;
        for (size_t j = i + 1; j < n; j++)
            if (shelf[j].published.year < shelf[best].published.year) best = j;
        if (best != i) { Book tmp = shelf[i]; shelf[i] = shelf[best]; shelf[best] = tmp; }
    }
    printf("oldest first: %s (%d)\n", shelf[0].title, shelf[0].published.year);
    return 0;
}
