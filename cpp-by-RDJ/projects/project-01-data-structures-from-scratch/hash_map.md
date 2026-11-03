# `hash_map.hpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`HashMap<K, V>` is a hash table with separate chaining: an array of buckets where each bucket is the head of a short linked chain of entries whose keys landed there. A key's hash picks the bucket, so lookup, insert and erase are O(1) on average, provided the hash spreads keys well and the table is kept below its load factor (here 0.75). It is the C++ twin of `java-by-RDJ/concepts/14-dsa-in-java/_4_HashMapWithChaining.java`.

## Full Line-by-Line Breakdown

### Layout
`buckets_` is a `Node**` obtained from `std::allocator<Node*>`; `bucket_count_` is always a power of two (8, 16, 32, ...) so `hash & (bucket_count_ - 1)` replaces a slow `%`. Each `Node` stores `std::pair<const K, V>`, the full hash (so rehashing never calls `Hash` again) and `next`. The table is allocated lazily on the first insert, so an empty map costs nothing.

### `mix` and the index
`std::hash<int>` is the identity in libstdc++, and a bit mask only looks at the low bits, so `mix` folds the high bits down (`h ^= h >> 32; h ^= h >> 16`). The demo measures what this does for keys that differ only in high bits:

```text
===== SECTION 3: HashMap (separate chaining, rehash at load factor 0.75) =====
bucket count after each rehash (measurement): 8 -> 16 -> 32 -> 64 -> 128 -> 256 -> 512 -> 1024 -> 2048 -> 4096 -> 8192 -> 16384
10000 sequential int keys: size=10000 buckets=16384 in_use=10000 load=0.610 rehashes=12 longest_chain=1
10000 seeded random int keys: size=10000 buckets=16384 in_use=7546 longest_chain=6
2000 keys that are multiples of 1024: buckets=4096 in_use=128 longest_chain=16
1000 keys, a hash that always returns 7: buckets=2048 in_use=1 longest_chain=1000   <- a linked list in disguise
   still correct: contains(999)=1 contains(1000)=0
word count via operator[]: to=2 be=2 or=1 not=1 size=4
```

Read the lines: ten thousand sequential keys give `longest_chain=1`; random keys give a longest chain of 6; and the line with a hash that always returns 7 shows `in_use=1 longest_chain=1000`, the map degenerating into one linked list while staying *correct*. Hashing quality is a performance property, not a correctness one.

### Lookup, `insert`, `insert_or_assign`, `operator[]`
All four call `find_node(key, hash)`: walk the chain, compare the stored hash first (cheap) and `KeyEqual` second. `insert` leaves an existing value alone (like `std::unordered_map::insert`); `insert_or_assign` overwrites; `operator[]` default-constructs a missing value, which gives the word-count idiom `++counts[word]` (the last demo line). New nodes are pushed on the front of their chain: O(1).

### Growth and rehash
Before adding, `grow_if_needed` checks `(size + 1) * 4 > bucket_count * 3` (integer maths for 0.75) and doubles the table. `rehash` allocates the new array *first* (if that throws nothing has changed), then relinks every existing node by its stored hash. Nodes are **not** reallocated, so references to elements survive a rehash (checked in `test_hash_map_references_survive_rehash`); iterators do not, same as `std::unordered_map`.

### Erase
`erase` walks with a pointer *to the pointer* (`Node**`) that leads to the current node. Unlinking is then one assignment, `*link_to_node = n->next`, for the head and the middle alike, with no special case.

### Iterators
`Iter<bool Const>` is a forward iterator: `++` moves to `node->next`, or, at the end of a chain, scans for the next non-empty bucket (using the node's stored hash to know its own bucket). Iteration order is bucket order, not insertion order. `iterator -> const_iterator` conversion is constrained exactly like the list's.

### Rule of five
Copy: delegate to a ctor that copies the hasher and equality, `reserve` the right bucket count, then insert every pair (a deep copy). Move: steal the array and counters, leaving the source empty and usable. Assignments use copy/move-and-swap. The destructor `clear()`s every chain, then frees the bucket array.

## Key Differences From Java
| Java `HashMap<K,V>` | C++ `HashMap<K,V,Hash,KeyEqual>` |
|---|---|
| `hashCode()` and `equals()` on the key object | `std::hash<K>` and `operator==` supplied as template parameters (or your own functors) |
| Forget `hashCode()` while overriding `equals()` and lookups silently miss | Same logic: an equal key must hash equal; the compiler cannot check it |
| Null keys allowed | No null concept for value keys |
| Large chains turn into trees (Java 8+) | Chains stay plain linked lists, so a bad hash really degrades to O(n) (the demo shows it) |
| Entries are objects, GC frees them | Each node is `new`/`delete`d by the map; the destructor and `erase` own that |

## Key Rules / Gotchas Recap
- Power-of-two table plus a bit mask needs a hash that mixes high bits.
- Allocate the new bucket array before touching the old one.
- Store the hash in the node: cheap comparisons and rehash without re-hashing.
- `operator[]` inserts; use `find` or `contains` when you only want to look.
- A constant hash is legal and correct, just O(n).

## Why This Structure Exists
Hash tables are the workhorse of symbol tables, caches, deduplication and feature counting in AI data pipelines, and their worst case (all keys colliding) is also a known denial-of-service vector, which is why hash quality and load factor are worth understanding before relying on a container.
