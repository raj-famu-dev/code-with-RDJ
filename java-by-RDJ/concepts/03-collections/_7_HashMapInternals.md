# `_7_HashMapInternals.java`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A hash map is an **array of buckets**. `key.hashCode()` is turned into an array index, so the right bucket is found in one step. This file builds a simplified `MiniMap` to make that visible; the real `java.util.HashMap` is more sophisticated.

## Full Line-by-Line Breakdown

### The `MiniMap` class
- `Node[] table = new Node[4]`: the buckets. Each `Node` holds a key, a value, and a link to the next node in the same bucket (a **chain**).
- `indexFor(key)`: `(hashCode & 0x7fffffff) % table.length` turns a hash into a bucket number. The mask removes the sign bit so the result is never negative.
- `put`: walk the bucket's chain; if `equals` finds the key, replace its value; otherwise add a new node at the front and increase `size`. If `size > capacity * 0.75`, call `resize()`.
- `get`: go straight to the bucket, then walk its chain using `equals`.
- `resize`: build a table twice as big and move **every** node into its new bucket, because `indexFor` depends on the table length.

### SECTION 1: The big idea
Jump to the right bucket instead of searching every entry.

### SECTION 2: Watch it grow
Six puts into a table that starts at capacity 4:
```
put apple      -> size=1, capacity=4
put banana     -> size=2, capacity=4
put cherry     -> size=3, capacity=4
put date       -> size=4, capacity=8     <- 4 > 4 * 0.75, so it doubled
put elderberry -> size=5, capacity=8
put fig        -> size=6, capacity=8
```
The bucket dump shows a real **collision**: `fig -> elderberry` share bucket 4. `get(date)` returns `4`; `get(grape)` returns `null`.

### SECTION 3: Collisions are normal
`"Aa".hashCode()` and `"BB".hashCode()` are both `2112`, yet a real `HashMap` keeps them as two separate keys (`1` and `2`). Equal hash codes do **not** mean equal objects; `equals()` makes the final decision inside the bucket.

### SECTION 4: Why `hashCode()` quality matters
If every key had the same hash, everything lands in one bucket and lookups slide from O(1) toward O(n).

### SECTION 5: The real `HashMap` (OpenJDK, Java 8+)
Default capacity 16, load factor 0.75, capacity always a power of two. It mixes the hash bits before choosing a bucket. When one bucket's chain gets long (threshold 8, with a big enough table) it is converted to a balanced tree, giving O(log n) worst case. These are implementation details, not specification guarantees.

### SECTION 6: Remember
`put`/`get` = `hashCode` → bucket → `equals` inside the bucket. Pre-size with `new HashMap<>(expected * 4 / 3 + 1)` when you know the count.

## Key Rules / Gotchas Recap
- Resizing is O(n) because every entry is re-placed
- Collisions are expected; correctness comes from `equals`
- A bad `hashCode` hurts speed, not correctness (a *missing* `hashCode` breaks correctness)

## Why This Structure Exists
Seeing the buckets turns "O(1) on average" from a slogan into something you can explain: array indexing for speed, chaining for collisions, resizing to keep chains short.
