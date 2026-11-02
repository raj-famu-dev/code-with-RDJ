# `_3_LinkedList.java`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`LinkedList` is a chain of nodes. Each node stores a value and links to its neighbours. Java's version is doubly linked and implements both `List` and `Deque`.

## Full Line-by-Line Breakdown

### The helper `Node` class
```java
static class Node { String value; Node next; ... }
```
A hand-made, singly linked node used only to **see** the mechanism. It is nested inside the class so it cannot collide with a `Node` in another file.

### SECTION 1: What it is
`add("b")`, `addFirst("a")`, `addLast("c")` produce `[a, b, c]`. Both `List` methods (`get`, `add(i, x)`) and `Deque` methods (`addFirst`, `removeLast`) are available.

### SECTION 2: Why `get(i)` is O(n)
Nodes are scattered in memory, so there is no formula to jump to an index. The loop hops `current = current.next` twice to reach index 2 (output: `Reached index 2 after 2 hops: c`). `list.get(2)` does the same walking internally. OpenJDK starts from whichever end is closer, which is an implementation detail.

### SECTION 3: The ends are cheap
`getFirst`, `getLast`, `addFirst`, `addLast`, `removeFirst`, `removeLast` are all O(1) because the list keeps references to both end nodes. After adding and removing both ends the list is back to `[a, b, c]`.

### SECTION 4: Trap: "insert in the middle is O(1)"
Only half true. Re-linking is O(1), but **finding the position** is O(n). `list.add(1, "x")` gives `[a, x, b, c]` after walking to index 1.

### SECTION 5: Removal while already positioned
An `Iterator` already holds its place, so `it.remove()` needs no search. After the loop removes `"x"`, the list is `[a, b, c]` again.

### SECTION 6: When to use it
Each element costs a node object (value + two links), so memory use is higher and cache behaviour is worse than an array. In practice `ArrayList` wins for lists and `ArrayDeque` wins for queues and stacks.

## Key Rules / Gotchas Recap
- `get(i)` is O(n), not O(1)
- "Constant-time insertion" only applies when you are **already at** the position
- Prefer `ArrayList` or `ArrayDeque` unless you have measured a reason

## Why This Structure Exists
Linked nodes make insertion and removal at a known position cheap without shifting elements. That is a real advantage in a few situations, but modern hardware favours contiguous arrays so strongly that `LinkedList` is rarely the best choice. Learning it explains **why** the trade-off exists.
