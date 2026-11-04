// Tags: #C #DataStructures #HashTable #Chaining #FNV | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* The hash table: an array of BUCKETS; each key hashes to one bucket;
   collisions in the same bucket chain. This is what Python's dict,
   Java's HashMap and C++'s unordered_map all are. */

typedef struct entry {
    char *key;                  /* table owns a COPY of the key */
    int value;
    struct entry *next;         /* the chain */
} Entry;

typedef struct {
    Entry **buckets;
    size_t capacity;
    size_t count;
    size_t chain_walks;         /* MEASUREMENT: how far lookups had to walk */
} Table;

/* strdup is POSIX, not C17: a portable copy helper instead. */
static char *dup_string(const char *s) {
    size_t n = strlen(s) + 1;
    char *copy = malloc(n);
    if (copy) memcpy(copy, s, n);
    return copy;
}

/* FNV-1a: small, fast, well-distributed string hash. */
static uint64_t fnv1a(const char *s) {
    uint64_t h = 1469598103934665603ULL;      /* FNV offset basis */
    while (*s) {
        h ^= (unsigned char)*s++;
        h *= 1099511628211ULL;                /* FNV prime */
    }
    return h;
}

static size_t bucket_of(const char *key, size_t capacity) {
    return (size_t)(fnv1a(key) & (uint64_t)(capacity - 1));   /* capacity is a power of 2 */
}

static int t_init(Table *t, size_t capacity) {
    t->buckets = calloc(capacity, sizeof *t->buckets);   /* zeroed: empty chains */
    if (!t->buckets) return -1;
    t->capacity = capacity;
    t->count = 0;
    t->chain_walks = 0;
    return 0;
}

static void t_free(Table *t) {
    for (size_t i = 0; i < t->capacity; i++) {
        Entry *e = t->buckets[i];
        while (e) { Entry *next = e->next; free(e->key); free(e); e = next; }
    }
    free(t->buckets);
    t->buckets = NULL;
    t->count = t->capacity = 0;
}

static int t_put(Table *t, const char *key, int value) {
    size_t b = bucket_of(key, t->capacity);
    /* update if the key already exists (one chain walk) */
    for (Entry *e = t->buckets[b]; e; e = e->next) {
        if (strcmp(e->key, key) == 0) { e->value = value; return 0; }
    }
    /* insert at the chain head */
    Entry *e = malloc(sizeof *e);
    if (!e) return -1;
    e->key = dup_string(key);                 /* table owns its copy */
    if (!e->key) { free(e); return -1; }
    e->value = value;
    e->next = t->buckets[b];
    t->buckets[b] = e;
    t->count++;
    return 0;
}

static int t_get(Table *t, const char *key, int *out) {
    size_t b = bucket_of(key, t->capacity);
    size_t walked = 0;
    for (Entry *e = t->buckets[b]; e; e = e->next) {
        walked++;
        if (strcmp(e->key, key) == 0) {
            t->chain_walks += walked;
            *out = e->value;
            return 0;
        }
    }
    t->chain_walks += walked;
    return -1;                                 /* not found */
}

int main(void) {
    Table t;
    if (t_init(&t, 16) != 0) return 1;        /* 16 buckets — deliberately small */

    /* 100 keys, ~6 per bucket: collisions are the NORM, not the exception. */
    char key[32];
    for (int i = 0; i < 100; i++) {
        snprintf(key, sizeof key, "key-%03d", i);
        t_put(&t, key, i * 7);
    }

    printf("100 keys in %zu buckets: count=%zu, load factor %.2f\n",
           t.capacity, t.count, (double)t.count / (double)t.capacity);

    /* Every key finds its value. */
    int v;
    int misses = 0;
    for (int i = 0; i < 100; i++) {
        snprintf(key, sizeof key, "key-%03d", i);
        if (t_get(&t, key, &v) != 0 || v != i * 7) misses++;
    }
    printf("all 100 lookups correct: %s\n", misses == 0 ? "yes" : "NO!");

    /* The measured price: chain walks per lookup. */
    printf("average chain walk per lookup: %.2f (load factor %.2f)\n",
           (double)t.chain_walks / 100.0, (double)t.count / (double)t.capacity);
    printf("=> O(1) only while the hash SPREADS keys and the load stays bounded;\n");
    printf("   real tables RESIZE when load factor ~0.75 (project-02 does).\n");

    /* Missing keys report, never crash. */
    printf("lookup of missing key: %s\n", t_get(&t, "nope", &v) == -1 ? "-1, checked" : "?!");
    t_free(&t);
    printf("freed all entries and buckets.\n");
    return 0;
}
