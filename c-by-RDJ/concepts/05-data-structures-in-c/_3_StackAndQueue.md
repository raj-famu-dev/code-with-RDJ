# `_3_StackAndQueue.c`

## Concept
The two access disciplines built on what we already have: the **stack** (LIFO) on the dynamic array's end — O(1) by construction; the **queue** (FIFO) as a **ring buffer** with indexes that wrap — O(1) with zero data movement.

## The Code

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct { int *data; size_t count, capacity; } Stack;

static int st_push(Stack *s, int v) {
    if (s->count == s->capacity && st_grow(s) != 0) return -1;
    s->data[s->count++] = v;
    return 0;
}
static int st_pop(Stack *s, int *out) {
    if (s->count == 0) return -1;
    *out = s->data[--s->count];
    return 0;
}

typedef struct { int *data; size_t capacity, count, head; } Queue;

static int q_push(Queue *q, int v) {
    if (q->count == q->capacity) return -1;
    q->data[(q->head + q->count) % q->capacity] = v;
    q->count++;
    return 0;
}
static int q_pop(Queue *q, int *out) {
    if (q->count == 0) return -1;
    *out = q->data[q->head];
    q->head = (q->head + 1) % q->capacity;
    q->count--;
    return 0;
}

int main(void) {
    Stack s;  st_init(&s);
    for (int i = 1; i <= 5; i++) st_push(&s, i);
    int v;
    while (st_pop(&s, &v) == 0) printf(" %d", v);

    Queue q;  q_init(&q, 8);
    for (int i = 1; i <= 5; i++) q_push(&q, i);
    while (q_pop(&q, &v) == 0) printf(" %d", v);
    return 0;
}
```

## Line-by-Line Breakdown

### Stack: push and pop at the END
`s->data[s->count++] = v` appends; `s->data[--s->count]` removes — both O(1), **no shifting ever happens** because both operations touch only the last slot. That's why a stack on a dynamic array is the natural marriage: the array's expensive middle-inserts never occur. Growth reuses topic 1's doubling.

### `st_pop` returns -1 on underflow
Popping an empty stack is a **reported condition**, not a crash — the function's return value carries the error, `out` carries the data (the Module 04 contract). The demo pops an empty stack on purpose.

### Queue: the ring buffer
FIFO from an array's *head* would shift everything left (O(n) per pop). The ring's fix: **keep the head index and wrap**.
- `tail` is computed: `(head + count) % capacity` — no separate tail field to desynchronize
- `q_pop` advances `head` by one, **modulo capacity** — the freed slot gets reused
- The demo wraps deliberately: pops move the head forward, then a push stores at an index "past the end" — modulo arithmetic folds it back

### Why modulo works
The data never moves; only the two indexes chase each other around the circle. Full is `count == capacity`; empty is `count == 0` — the one-slot ambiguity of naive head==tail designs is avoided by tracking `count`.

### What each structure is for
- **Stack:** undo, expression evaluation, DFS, call stacks — anything LIFO
- **Queue:** scheduling, BFS, buffering — anything FIFO (the producer/consumer of Module 05's concurrency cousins in the Java/C++ labs)

## Traps
- The classic ring-buffer bug: using `head == tail` for both "empty" and "full" — they're the same condition; that's why `count` exists.
- Fixed-capacity queue here returns -1 when full — real ones grow or block (the `BlockingQueue` lesson from the Java lab).
- Stack on a dynamic array is the standard; queue on a *shifting* array is the O(n) mistake.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _3_StackAndQueue.c && ./demo
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo_s _3_StackAndQueue.c && ./demo_s
```

## Why This Structure Exists
Stack and queue are the two disciplines every algorithm needs (DFS/BFS are literally "stack vs queue"). Building them on the dynamic array and the ring shows that data structures are *policies over memory*, not magic.
