// Tags: #C #DataStructures #LinkedList | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>

/* The linked list: nodes allocated one at a time, chained by pointers.
   Doubly-linked here (prev + next) — like Java's LinkedList. */

typedef struct node {
    int value;
    struct node *prev;      /* NULL at the head */
    struct node *next;      /* NULL at the tail */
} Node;

typedef struct {
    Node *head;
    Node *tail;
    size_t count;
} List;

/* push at the TAIL: O(1), because we track the tail. */
static int list_push_back(List *l, int value) {
    Node *n = malloc(sizeof *n);
    if (!n) return -1;
    n->value = value;
    n->next = NULL;
    n->prev = l->tail;

    if (l->tail) l->tail->next = n; else l->head = n;   /* first node ever */
    l->tail = n;
    l->count++;
    return 0;
}

/* pop from the HEAD: O(1). */
static int list_pop_front(List *l, int *out) {
    if (l->head == NULL) return -1;                     /* empty */
    Node *victim = l->head;
    *out = victim->value;
    l->head = victim->next;
    if (l->head) l->head->prev = NULL; else l->tail = NULL;
    free(victim);
    l->count--;
    return 0;
}

/* O(n) indexed access — the price of links: walk from the nearer end. */
static Node *list_at(List *l, size_t i) {
    if (i >= l->count) return NULL;
    Node *n = (i < l->count / 2) ? l->head : l->tail;
    size_t remaining = (i < l->count / 2) ? i : l->count - 1 - i;
    for (size_t j = 0; j < remaining; j++) n = n->prev;  /* walking from tail goes backward */
    return n;
}

static void list_free(List *l) {
    Node *n = l->head;
    while (n) {
        Node *next = n->next;
        free(n);
        n = next;
    }
    l->head = l->tail = NULL;
    l->count = 0;
}

int main(void) {
    List l = { 0 };
    for (int i = 1; i <= 5; i++) list_push_back(&l, i * 10);

    printf("count=%zu. pop:", l.count);
    int v;
    while (list_pop_front(&l, &v) == 0) printf(" %d", v);
    printf("\n(FIFO: push at tail, pop at head — both O(1))\n");

    for (int i = 1; i <= 5; i++) list_push_back(&l, i * 10);
    Node *third = list_at(&l, 2);
    printf("element 2 (walked from the nearer end): %d\n", third->value);
    printf("O(1) insert/remove WITH the node in hand; O(n) to FIND it. That's the trade.\n");

    list_free(&l);
    printf("freed every node. no leaks.\n");
    return 0;
}
