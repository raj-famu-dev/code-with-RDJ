// Tags: #C #DataStructures #Stack #Queue | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>

/* STACK (LIFO) on the dynamic array: push/pop at the END — both O(1),
   no shifting ever. This is what Java's Stack/ArrayDeque really are. */
typedef struct {
    int *data;
    size_t count, capacity;
} Stack;

static int st_init(Stack *s) {
    s->capacity = 8;
    s->count = 0;
    s->data = malloc(s->capacity * sizeof *s->data);
    return s->data ? 0 : -1;
}
static void st_free(Stack *s) { free(s->data); s->data = NULL; }
static int st_grow(Stack *s) {
    s->capacity *= 2;
    int *b = realloc(s->data, s->capacity * sizeof *b);
    if (!b) return -1;
    s->data = b;
    return 0;
}
static int st_push(Stack *s, int v) {
    if (s->count == s->capacity && st_grow(s) != 0) return -1;
    s->data[s->count++] = v;
    return 0;
}
static int st_pop(Stack *s, int *out) {
    if (s->count == 0) return -1;        /* underflow: the caller's error to handle */
    *out = s->data[--s->count];
    return 0;
}

/* QUEUE (FIFO) as a RING BUFFER: fixed capacity, head and tail indexes
   wrap around with modulo. Enqueue/dequeue both O(1), zero data movement. */
typedef struct {
    int *data;
    size_t capacity, count, head;   /* tail = (head + count) % capacity */
} Queue;

static int q_init(Queue *q, size_t cap) {
    q->data = malloc(cap * sizeof *q->data);
    q->capacity = cap; q->count = 0; q->head = 0;
    return q->data ? 0 : -1;
}
static void q_free(Queue *q) { free(q->data); q->data = NULL; }
static int q_push(Queue *q, int v) {
    if (q->count == q->capacity) return -1;          /* full (fixed-cap demo) */
    q->data[(q->head + q->count) % q->capacity] = v;
    q->count++;
    return 0;
}
static int q_pop(Queue *q, int *out) {
    if (q->count == 0) return -1;
    *out = q->data[q->head];
    q->head = (q->head + 1) % q->capacity;           /* wrap */
    q->count--;
    return 0;
}

int main(void) {
    /* Stack: LIFO — reverse order out. */
    Stack s;
    if (st_init(&s) != 0) return 1;
    for (int i = 1; i <= 5; i++) st_push(&s, i);
    printf("stack pop:");
    int v;
    while (st_pop(&s, &v) == 0) printf(" %d", v);
    printf("  (LIFO)\n");
    st_free(&s);

    /* Queue: FIFO — arrival order out. */
    Queue q;
    if (q_init(&q, 8) != 0) return 1;
    for (int i = 1; i <= 5; i++) q_push(&q, i);
    printf("queue pop:");
    while (q_pop(&q, &v) == 0) printf(" %d", v);
    printf("  (FIFO)\n");

    /* Ring-buffer wraparound, demonstrated: wrap the head around. */
    for (int i = 10; i <= 15; i++) q_push(&q, i);   /* fills slots */
    for (int i = 0; i < 4; i++) q_pop(&q, &v);      /* moves head forward */
    q_push(&q, 99);                                  /* tail wraps past the end */
    printf("after wraparound, next pops:");
    while (q_pop(&q, &v) == 0) printf(" %d", v);
    printf("\n(the 99 stored in a wrapped slot — no data ever moved)\n");
    q_free(&q);

    /* Underflow is a REPORTED condition, not a crash. */
    Stack empty;
    st_init(&empty);
    printf("pop from empty stack: %s (checked, no crash)\n",
           st_pop(&empty, &v) == -1 ? "returned -1" : "?!");
    st_free(&empty);
    return 0;
}
