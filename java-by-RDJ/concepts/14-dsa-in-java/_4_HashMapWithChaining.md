> 📘 Reference material drafted with Claude. Not yet learned: retype `_4_HashMapWithChaining.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Hash Map with Chaining

## Concept

A hash map turns a key into an array index so lookups do not scan. Different keys can land on the same index (a **collision**), so each array slot (**bucket**) holds a small linked **chain** of entries. `03-collections/_7_HashMapInternals` shows the minimal idea; this file adds resizing, removal, null keys and an oracle test.

## Big-O (n = entries)

| Operation | Average | Worst case |
|---|---|---|
| `get`, `put`, `remove`, `containsKey` | **O(1)** | **O(n)** (every key in one bucket: a linked list) |
| resize | O(n), but rare, so `put` is **O(1) amortized** | O(n) |
| iteration | O(capacity + n) | same |

"Average O(1)" **depends on two things you control**: a `hashCode` that spreads keys, and a table that grows so the load factor stays at or below 0.75.

## Full Line-by-Line Breakdown

**Index calculation.** `h = key.hashCode()`, then `h ^ (h >>> 16)` mixes the high bits into the low bits, then `index = hash & (table.length - 1)`. Because the table length is always a power of two, the bitmask is equivalent to `% length` but always non-negative (a `%` on a negative hash gives a negative index, one of the "break on purpose" tasks).

**`put`.** Walk the chain. If a key with the same hash that is `equals` is found, replace the value and return the old one (size unchanged). Otherwise insert a new node at the **front** of the chain (O(1)), increment `size`, and resize if `size > 0.75 * capacity`.

**`remove`.** Walk the chain remembering `previous`; unlink the matching node (first-node case and middle/end case are different).

**`resize`.** Double the table, then move every node into its new bucket using the **stored** hash (no `hashCode` calls). Save `n.next` *before* re-linking the node or the rest of the chain is lost.

**Null keys.** `spread(null)` is 0 and comparisons use `n.key == key || key.equals(n.key)`, so null works, like `HashMap`.

Real output:

```
get(Ada) = 36, get(Zed) = null, size = 3
put(Ada, 37) returned the old value: 36, size still 3
remove(Linus) = 55, containsKey(Linus) = false
a null key works here (like HashMap): -1
after 1000 puts: entries=1000, buckets=2048, buckets in use=1000, longest chain=1, resizes=8
all 1000 still found after rehashing: true
500 keys with hashCode() == 42:   entries=500, buckets=1024, buckets in use=1, longest chain=500   <- one giant chain: a linked list
500 keys with a proper hashCode: entries=500, buckets=1024, buckets in use=500, longest chain=1
equals() overridden but not hashCode(): get(new ForgetfulKey("ada")) = null   <- the equal key hashes elsewhere
oracle test: 50000 random operations match java.util.HashMap: true (final size 1048)
```

**Honest reading of those numbers.**
- 1000 puts: 8 resizes (8 to 16 to ... to 2048) and a longest chain of 1. That "perfect" result is partly because the keys are the **sequential integers** 0..999, whose hashes are themselves. Real keys (strings, objects) collide more. Do not generalise "chain length 1" from this line.
- `BadKey` with `hashCode() == 42` is legal Java and ends up with **one bucket in use and a chain of 500**: the map degraded into a linked list, so every `get` is O(n).
- `ForgetfulKey` overrides `equals` but not `hashCode`. The lookup key is "equal" but hashes to a different bucket, so `get` returns `null`. The compiler (`-Xlint:all`) deliberately warns about this class: `[overrides] ... overrides equals, but neither it nor any superclass overrides hashCode`. That one warning is **expected**; it is the demo.

**Oracle test.** 50,000 random `put` / `remove` / `get` operations against `java.util.HashMap` (reference only). Every return value and the size must match after every step.

## Key Rules

1. Equal objects **must** have equal hash codes. Override `equals` and `hashCode` together.
2. Keys must not change in a way that alters `hashCode` while they are in the map.
3. Power-of-two capacity plus a bitmask replaces `%`.
4. Resize before chains get long: load factor 0.75 is the JDK's default trade-off between memory and speed.
5. Money, IDs and anything you hash should be immutable.

## Gotchas Recap

- Equal-but-differently-hashed keys are *silently* lost, not an error.
- A constant or poor `hashCode` is legal and catastrophic for performance.
- Worst case O(n) is also the **denial-of-service** concern behind hash-flooding attacks. Java 8+ `HashMap` converts a long chain into a balanced tree to bound the damage (this file does not).
- Iteration order of a hash map is not defined; do not depend on it.

## Why This Structure Exists

The hash map is the single most-used structure in interviews and in production code. Seeing a chain of 500 appear on screen is what makes "write a good `hashCode`" stop being a rule and start being a performance argument you can make.
