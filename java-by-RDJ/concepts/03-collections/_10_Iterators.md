# `_10_Iterators.java`

> Walkthrough drafted with Claude. Check it against your own understanding and rewrite it in your own words.

## Concept
An `Iterator` is a cursor that walks a collection one element at a time. The for-each loop is shorthand for it. Understanding it explains `ConcurrentModificationException`.

## Full Line-by-Line Breakdown

### The `Countdown` class
A class that implements `Iterable<Integer>`, so it works in for-each. Its `iterator()` returns an anonymous `Iterator` with a `next` counter: `hasNext()` is `next > 0`, and `next()` returns the value then decrements it (throwing `NoSuchElementException` when exhausted).

### SECTION 1: The basics
`hasNext()` asks "is there another?"; `next()` returns it and advances. Visits `a, b, c, d` in order.

### SECTION 2: Safe removal with `it.remove()`
The iterator removes the element it **just returned** and keeps its own position correct. Removing `"b"` leaves `[a, c, d]`.

### SECTION 3: Fail-fast
`ArrayList` counts structural changes (`modCount`); the iterator checks it on every `next()`. Removing `"a"` inside a for-each makes the next `next()` throw `ConcurrentModificationException`, which the code catches.

### SECTION 4: Trap: the case that does not throw
Remove the **second-to-last** element and `hasNext()` returns `false` before the check ever runs. No exception, but the last element is skipped silently. Output: `Visited [a, b] - "c" was silently skipped`. Fail-fast is best effort, never a guarantee.

### SECTION 5: Three safe ways to remove while looping
1. `removeIf(n -> n % 2 == 0)` → `[1, 3, 5]` (shortest and clearest)
2. Loop over a **copy**, change the original → `[1, 5]`
3. Explicit `Iterator` + `it.remove()` (Section 2)

### SECTION 6: `ListIterator`
Goes forward **and** backward and can `set` and `add`. For `[x, y, z]` it replaces `y` with `Y` and inserts `y2` after it; walking backwards prints `z y2 Y x`.

### SECTION 7: Your own class in for-each
`for (int n : new Countdown(3))` prints `3 2 1`.

## Key Rules / Gotchas Recap
- Remove during iteration only via `it.remove()`, `removeIf`, or a copy
- A "no exception" run does **not** prove a loop was safe (Section 4)
- Implement `Iterable` to make your own type work in for-each

## Why This Structure Exists
Iterators let one loop syntax work over lists, sets, queues, and your own types without knowing how each stores its data.
