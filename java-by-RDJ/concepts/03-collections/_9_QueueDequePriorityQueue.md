# `_9_QueueDequePriorityQueue.java`

> Walkthrough drafted with Claude. Check it against your own understanding and rewrite it in your own words.

## Concept
A `Queue` holds items waiting to be processed. `Deque` works at both ends (so it can also be a stack). `PriorityQueue` always hands back the "best" item first rather than the oldest.

## Full Line-by-Line Breakdown

### The `Task` record
`record Task(String name, int priority) {}`: a compact immutable data class used in Section 6. It prints as `Task[name=..., priority=...]`.

### SECTION 1: FIFO
`offer` adds at the back, `peek` looks at the front without removing, `poll` removes the front. After polling `first`, the queue is `[second, third]`.

### SECTION 2: Two families of methods
| Throws on failure | Returns a special value |
|---|---|
| `add(x)` | `offer(x)` |
| `remove()` | `poll()` |
| `element()` | `peek()` |

On an empty queue `poll()` and `peek()` return `null`, while `remove()` throws `NoSuchElementException` (caught in the code).

### SECTION 3: Deque as a stack
```java
stack.push(1); stack.push(2); stack.push(3);
stack.pop();   // 3
```
Last in, first out: `pop` gives `3`, then `2`. Prefer `ArrayDeque` over the legacy `Stack` class (synchronized and built on `Vector`). `offerFirst` / `offerLast` / `pollLast` work at both ends: `[A, B, C]`, `pollLast` gives `C`. `ArrayDeque` rejects `null`, because `poll()` uses `null` to mean "empty".

### SECTION 4: `PriorityQueue`
Backed by a binary heap. `poll()` returns the smallest element regardless of insertion order. Adding `5, 1, 4, 2, 3` polls out as `1 2 3 4 5`. `offer`/`poll` are O(log n); `peek` is O(1).

### SECTION 5: Trap: printing a `PriorityQueue`
Output: `[1, 2, 4, 5, 3]`. That is the heap's internal layout, **not** sorted order. Only the first element is guaranteed to be the smallest.

### SECTION 6: Custom order
`new PriorityQueue<>(Comparator.reverseOrder())` makes a max-heap (`peek` is `5`). With `Comparator.comparingInt(Task::priority)`, tasks come out as `fix outage` (1), `reply to email` (2), `write report` (3).

### SECTION 7: Choosing
FIFO processing → `ArrayDeque` as a `Queue`. Undo history or call stack → `ArrayDeque` as a `Deque`. Best-first processing → `PriorityQueue`.

## Key Rules / Gotchas Recap
- `poll`/`peek` return `null` when empty; `remove`/`element` throw
- Use `ArrayDeque` for both queues and stacks
- Never iterate a `PriorityQueue` expecting sorted order; poll it instead

## Why This Structure Exists
Many problems are "do the next thing": a print queue, an undo stack, a scheduler. These three types model that directly, and `PriorityQueue` powers algorithms like Dijkstra later in `14-dsa-in-java`.
