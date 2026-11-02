> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Stack and Queue

## Concept

A **stack** is last-in-first-out (a pile of plates: `push`, `pop`, `peek`). A **queue** is first-in-first-out (a line: `enqueue` at the back, `dequeue` from the front). Both are *restricted interfaces*: you give up random access so that every operation can be **O(1)**.

Three implementations here: a stack on an array, a queue on linked nodes, and a queue on a **ring buffer** (circular array).

## Big-O

| Structure | Operations | Time |
|---|---|---|
| `ArrayStack` | `push` | **O(1) amortized** (doubling resize) |
| | `pop`, `peek`, `isEmpty`, `size` | **O(1)** |
| `LinkedQueue` | `enqueue`, `dequeue`, `peek` | **O(1)** worst case (no resize ever) |
| `RingQueue` | `dequeue`, `peek` | **O(1)** |
| | `enqueue` | **O(1) amortized** |
| naive array queue (dequeue from index 0) | `dequeue` | **O(n)**, which is the problem the ring solves |

Memory: all O(n). Linked nodes cost an extra object per element; arrays can waste up to half their capacity.

## Full Line-by-Line Breakdown

**`ArrayStack`.** The top of the stack is `data[size - 1]`. `push` doubles when full; `pop` decrements `size` and **nulls the slot** so the removed object can be garbage-collected.

**`LinkedQueue`.** Keeps `head` (front, for `dequeue`) and `tail` (back, for `enqueue`). When `dequeue` empties the queue it must set `tail = null` too, otherwise `tail` still points at a removed node and the next `enqueue` attaches to a ghost.

**`RingQueue`.** Removing from index 0 of a plain array would shift everything. A ring just moves a `head` index forward. The back is `(head + size) % data.length`, so it **wraps** around the end of the array and reuses the freed slots at the front. Real output:

```
full:             [A B C D] head=0 size=4
after 2 dequeues: [_ _ C D] head=2 size=2
E and F WRAPPED:  [E F C D] head=2 size=4   (back of the queue is at the start of the array)
grew and unwrapped: [C D E F G _ _ _] head=0 size=5
dequeued in order: CDEFG
```

Read the third line: the queue is logically `C D E F`, but physically `E F` sit in slots 0 and 1. Growing therefore **cannot** use a plain `arraycopy`. `grow()` copies in *logical* order (`data[(head + i) % length]`) into the new array starting at 0 and resets `head = 0` ("unwrapping"). The fourth line shows that result.

**Classic uses (real output):**

```
balanced "{[()]}"  : true
balanced "{[(])}"  : false
balanced "(("      : false
postfix "3 4 + 2 *"     = 14
postfix "5 1 2 + 4 * + 3 -" = 14
survivor among 7 with k=3: person 4
survivor among 41 with k=3: person 31
```

- **Balanced brackets (stack).** Push every opener; each closer must match the most recent opener. The most recent unmatched thing is exactly what a stack gives you.
- **Postfix evaluation (stack).** Operands are pushed; an operator pops the **right** operand first, then the left, and pushes the result. Popping them in the wrong order breaks `5 3 -`.
- **Josephus (queue).** Rotate the front to the back `k - 1` times, then remove the next one. Person 4 survives with 7 people and k = 3; 31 survives with 41 (the well-known Josephus answer for that case).

**The oracle test.** 20,000 random operations run against both queues and the stack and against `java.util.ArrayDeque` (used only as a reference, never inside the structures). One bug was caught while writing this file: the stack comparison used `==` on two `Integer` objects, which compares **references** and is only reliable for small cached values. It was changed to `.equals`.

## Key Rules

1. Stack = the thing you most recently saw must be undone first (undo, brackets, call stack, DFS).
2. Queue = fairness and order of arrival (BFS, task scheduling, buffering).
3. A ring buffer is a queue on an array without O(n) shifting.
4. When a ring grows, **unwrap** it; do not copy it blindly.
5. Compare `Integer` objects with `.equals`, never `==`.

## Gotchas Recap

- `tail` not reset when a linked queue empties.
- `head + size` without `% length` walks off the array.
- `ArrayDeque` is the JDK's recommended stack and queue. `java.util.Stack` is a legacy synchronized class; avoid it in new code.
- A "full" ring and an "empty" ring both have `head == tail` if you track only two indices; tracking `size` (as here) avoids that ambiguity.

## Why This Structure Exists

These two interfaces power half the rest of the folder: recursion is a stack, BFS is a queue, a heap is a smarter queue. Building the ring buffer is the best exercise here because it is the one place where index arithmetic can go quietly wrong.
