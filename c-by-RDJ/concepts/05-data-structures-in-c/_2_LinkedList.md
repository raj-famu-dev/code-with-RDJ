# `_2_LinkedList.c`

## Concept
The linked list: nodes chained by pointers, each allocated separately. O(1) insert/remove when you hold the node; O(n) to find it. The doubly-linked version (prev + next) — the same design as Java's `LinkedList` — is built here from scratch.

## The Code

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct node {
    int value;
    struct node *prev;
    struct node *next;
} Node;

typedef struct {
    Node *head;
    Node *tail;
    size_t count;
} List;

static int list_push_back(List *l, int value) {
    Node *n = malloc(sizeof *n);
    if (!n) return -1;
    n->value = value;
    n->next = NULL;
    n->prev = l->tail;
    if (l->tail) l->tail->next = n; else l->head = n;
    l->tail = n;
    l->count++;
    return 0;
}

static int list_pop_front(List *l, int *out) {
    if (l->head == NULL) return -1;
    Node *victim = l->head;
    *out = victim->value;
    l->head = victim->next;
    if (l->head) l->head->prev = NULL; else l->tail = NULL;
    free(victim);
    l->count--;
    return 0;
}

int main(void) {
    List l = { 0 };
    for (int i = 1; i <= 5; i++) list_push_back(&l, i * 10);
    printf("count=%zu. pop:", l.count);
    int v;
    while (list_pop_front(&l, &v) == 0) printf(" %d", v);
    printf("\n");
    list_free(&l);
    return 0;
}
```

## Line-by-Line Breakdown

### The node: `struct node *prev, *next`
Self-referential struct — the tag is required (Module 03's typedef lesson) because the struct contains pointers to *itself*. Each node is a separate `malloc`: the list's memory is scattered by design.

### The list struct: `head / tail / count`
Head and tail are tracked so both ends are O(1) — that's what makes the list a queue for free (topic 3). `count` avoids the O(n) length walk.

### `list_push_back` — the four-pointer dance
Link the new node: `n->prev = tail`, `tail->next = n` (or `head = n` if first). **Updating both directions** is where bugs live — forget `head->prev` and the list looks fine walking forward but breaks walking back.

### `list_pop_front`
The out-parameter pattern (`int *out`): the function signals failure with its return and delivers the value through the pointer — the C idiom for "returning" two things.

### `list_at` — O(n) indexed access
Walk from whichever end is nearer. This is the list's structural tax: `array[i]` is one load; `list[i]` is i pointer-chases. The demo prints the tradeoff in words because it's the whole point.

### `list_free`
The standard walk-and-free: save `next` **before** `free` (reading `n->next` after `free` is the use-after-free from Module 02). One malloc per node means one free per node.

## Traps
- Forgetting one direction of a doubly-link update — "the list works forward, breaks backward" bugs.
- `free` in a loop reading `n->next` afterward — always stash `next` first.
- Sentinel-vs-NULL designs differ across codebases — read which one you're in before editing.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _2_LinkedList.c && ./demo
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo_s _2_LinkedList.c && ./demo_s
```

## Why This Structure Exists
The list is the structure where **pointers are the design**: each node's location is independent, so insertion never moves other data (contrast topic 1's realloc copies). Choosing list vs array is C's fundamental trade — and the C++/Java labs' `list` vs `vector`/`ArrayList` debate is exactly this file.
