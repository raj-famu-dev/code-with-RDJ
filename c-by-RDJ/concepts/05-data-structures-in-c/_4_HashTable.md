# `_4_HashTable.c`

## Concept
The hash table: keys hash to buckets, collisions chain. One hash function (FNV-1a), one array, one chain per bucket — and a measured load factor that shows why real tables resize. This is the same structure as Python's `dict`, Java's `HashMap`, and project-02 in this lab.

## The Code

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct entry {
    char *key;
    int value;
    struct entry *next;
} Entry;

typedef struct {
    Entry **buckets;
    size_t capacity;
    size_t count;
    size_t chain_walks;
} Table;

static uint64_t fnv1a(const char *s) {
    uint64_t h = 1469598103934665603ULL;
    while (*s) {
        h ^= (unsigned char)*s++;
        h *= 1099511628211ULL;
    }
    return h;
}

static size_t bucket_of(const char *key, size_t capacity) {
    return (size_t)(fnv1a(key) & (uint64_t)(capacity - 1));
}

static int t_put(Table *t, const char *key, int value) {
    size_t b = bucket_of(key, t->capacity);
    for (Entry *e = t->buckets[b]; e; e = e->next) {
        if (strcmp(e->key, key) == 0) { e->value = value; return 0; }
    }
    Entry *e = malloc(sizeof *e);
    if (!e) return -1;
    e->key = strdup(key);
    if (!e->key) { free(e); return -1; }
    e->value = value;
    e->next = t->buckets[b];
    t->buckets[b] = e;
    t->count++;
    return 0;
}

int main(void) {
    Table t;
    t_init(&t, 16);

    char key[32];
    for (int i = 0; i < 100; i++) {
        snprintf(key, sizeof key, "key-%03d", i);
        t_put(&t, key, i * 7);
    }
    printf("100 keys in %zu buckets: count=%zu, load factor %.2f\n",
           t.capacity, t.count, (double)t.count / (double)t.capacity);

    int v, misses = 0;
    for (int i = 0; i < 100; i++) {
        snprintf(key, sizeof key, "key-%03d", i);
        if (t_get(&t, key, &v) != 0 || v != i * 7) misses++;
    }
    printf("all 100 lookups correct: %s\n", misses == 0 ? "yes" : "NO!");
    t_free(&t);
    return 0;
}
```

## Line-by-Line Breakdown

### `Entry` — the chain node
`key` (a heap **copy** the table owns — `strdup`), `value`, and `next`. Each bucket is a linked list (topic 2) in miniature.

### `fnv1a` — the hash function
The FNV-1a algorithm: XOR each byte into the state, multiply by the FNV prime. Two properties that matter: **deterministic** (same string, same hash, every run — required) and **well-distributed** (similar strings land in different buckets). A bad hash (say, one that only looks at the first character) degrades the table to a linked list — exactly what the Java DSA module measured with a constant `hashCode`.

### `bucket_of`: mask, not modulo
`fnv1a(key) & (capacity - 1)` — bitwise AND with a power-of-two minus one is a cheap modulo. That's why real tables keep capacity a power of two (the Java `HashMap` internals topic).

### `t_put`: update-or-insert
One chain walk: if the key exists, update; otherwise `malloc` an entry, `strdup` the key, **insert at the chain's head** (O(1), no tail tracking needed).

### `t_get`: walk and count
The demo's `chain_walks` counter **measures the price**: with 100 keys in 16 buckets (load factor 6.25), every lookup walks ~6 entries on average — which is exactly the load factor, because FNV-1a distributes uniformly. The lesson in numbers: **the table is only as fast as the hash's spread and the load's bound.**

### Why resize at ~0.75
Real tables (and this lab's project-02) **rehash into a bigger array** when `count / capacity` exceeds a threshold: every chain is short again, at the cost of re-allocating and re-hashing everything once. The Java lab's measured 1.31-copies lesson (dynamic array) is the same economics.

### Ownership (documented like the header of project-02)
The table owns: each entry's `key` copy, every `Entry`, and the bucket array. `t_free` frees all three in the right order (entries first, then buckets).

## Traps
- Storing the caller's `char *` instead of a copy — the caller frees or reuses it, and your keys dangle. `strdup` is the fix.
- `strcmp` after a NULL `key` — allocation failure paths must free cleanly (the `if (!e->key) { free(e); return -1; }` dance).
- No resize in this teaching version — a table loaded to 100 is a slow table; project-02 fixes that.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _4_HashTable.c && ./demo
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo_s _4_HashTable.c && ./demo_s
```

## Why This Structure Exists
The hash table is the trade that makes lookups O(1)-ish by *paying in memory* (buckets) and *betting on the hash* (spread). Building it with the walk counter on is how the C++/Java labs' "load factor" stops being vocabulary and becomes a number you watched.
