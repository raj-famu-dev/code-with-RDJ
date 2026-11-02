> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Concurrent Collections

## Concept

`HashMap` and `ArrayList` have no locking: two threads changing one at once can lose updates or corrupt it. `java.util.concurrent` has versions built for sharing. (The file deliberately does **not** run a broken `HashMap` demo, because its failures are unpredictable.)

## Full Line-by-Line Breakdown

**Section 2: `ConcurrentHashMap`.** Thread-safe without locking the whole map. The trick is the **atomic methods**: `map.put(k, map.get(k) + 1)` is still a race; `map.merge(k, 1, Integer::sum)` is not.

```
ConcurrentHashMap merge: 40000 (expected 40000)
after putIfAbsent: {hits=40000, misses=0}
NullPointerException: ConcurrentHashMap does not allow null keys or values
```

**Section 3: the `ConcurrentModificationException` trap.** Adding to an `ArrayList` while looping over it fails, even in one thread.

**Section 4: `CopyOnWriteArrayList`.** Each write copies the array; iterators use the snapshot they started with, so the loop above is allowed and still sees the old 3 items:

```
CopyOnWriteArrayList after the loop: [1, 2, 3, 99]
```

Good for rarely changed, often iterated lists (like listeners); bad for heavy writing.

**Section 5: `BlockingQueue` (`ArrayBlockingQueue`).** The `_7` buffer, ready-made: `put` waits when full, `take` waits when empty. Poison value `-1` ends the consumer:

```
BlockingQueue delivered: [1, 2, 3, 4, 5, 6, 7, 8]
poll(50 ms) on an empty queue: null
offer("y") on a full queue:   false
```

**Section 6: `CountDownLatch(3)`.** Each worker calls `countDown()`; `await(2, SECONDS)` returns `true` once it reaches 0. Single-use.

**Section 7:** `Collections.synchronizedList` is the old way: it locks the whole list, and iterating still needs a manual `synchronized` block.

## Key Rules

1. Use the atomic methods (`merge`, `compute`, `putIfAbsent`), not get-then-put.
2. `ConcurrentHashMap` forbids null keys and values.
3. Prefer `BlockingQueue` over hand-written wait/notify.
4. Use timeouts (`poll`, `offer`, `await`) so nothing waits forever.

## Gotchas Recap

- Thread-safe collection does not make compound actions safe.
- `CopyOnWriteArrayList` iterators do not show later changes.
- A latch cannot be reset.

## Why This Structure Exists

It walks from "why plain collections fail" to the specific replacement for each common need: map, list, queue, countdown.
