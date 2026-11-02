> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Linked Lists (singly, then doubly)

## Concept

A linked list stores each element in a **node** that holds a reference to the next node (singly) or to both neighbours (doubly). There is no index arithmetic: to reach position `i` you walk `i` links. In return, inserting or removing next to a node you already hold is just pointer changes, with no shifting.

## Big-O (n = size)

| Operation | Singly (head only) | Doubly (head and tail) |
|---|---|---|
| `addFirst` / `removeFirst` | **O(1)** | **O(1)** |
| `addLast` | **O(n)** (walk to the end) | **O(1)** |
| `removeLast` | O(n) | **O(1)** |
| `get(i)`, `insert(i)`, `remove(i)` | **O(n)** | O(n) (walks from the nearer end, still O(n)) |
| remove a node you already hold | O(n) (need its predecessor) | **O(1)** |
| `contains` | **O(n)** | O(n) |
| `reverse` | **O(n)** time, **O(1)** space | n/a here |
| memory per element | one node: value + 1 reference (plus object header) | value + 2 references |

Versus an array list: no O(1) random access, more memory per element, and poor CPU-cache behaviour because nodes are scattered in memory. In practice an `ArrayList` beats a `LinkedList` for most workloads.

## Full Line-by-Line Breakdown

**Singly: `addFirst`.** New node's `next` = old head, then `head` = new node. Order matters only so that you never lose the old head.

**`insert(i)`.** Find the node *before* position `i`, then:
1. `node.next = before.next` (the new node points at what followed)
2. `before.next = node` (the predecessor points at the new node)

Swap those two lines and `before.next` already points at the new node, so step 1 makes the new node point at *itself* and the rest of the list is lost. That is the first "break on purpose" exercise.

**`remove(i)`.** `before.next = before.next.next` skips over the removed node. The removed node becomes unreachable and the GC takes it.

**`reverse`.** Three references (`previous`, `current`, `next`). Save `next` *before* flipping `current.next`, otherwise you cut off the rest of the list.

**`middle`.** Fast and slow pointers: `fast` moves two steps per `slow` step, so when `fast` hits the end `slow` is in the middle. One pass, O(1) space.

**`hasCycle` (Floyd's tortoise and hare).** Same two pointers. If there is a loop, `fast` eventually laps `slow` and they meet; if not, `fast` falls off the end.

**Doubly: the edge cases.** `removeFirst` must reset **both** ends when the list becomes empty (`if (head == null) tail = null`), otherwise `tail` still points at a removed node and the next `addLast` corrupts the list. `get(i)` starts from `head` or `tail`, whichever is nearer.

Real output:

```
=== singly linked list ===
list:             1 -> 2 -> 3 -> 4 -> 5  (size 5)
insert(2, 99):    1 -> 2 -> 99 -> 3 -> 4 -> 5
remove(2) returned 99, list is now: 1 -> 2 -> 3 -> 4 -> 5
middle():         3
reversed:         5 -> 4 -> 3 -> 2 -> 1
contains(3) = true, contains(42) = false
IndexOutOfBoundsException: index 9, size 5
NoSuchElementException: list is empty
hasCycle (normal list): false
hasCycle (5 points back to 2): true
=== doubly linked list ===
forward:  a <-> b <-> c <-> d
backward: d <-> c <-> b <-> a
removeFirst returned a, removeLast returned d, list is now: b <-> c
get(0) = b, get(1) = c
emptied: (empty), adding after emptying works: true
oracle test: 5000 random operations, singly and doubly match ArrayList: true
```

**Note on the print lines.** Each removal prints the *returned* value first and the *remaining* list second, in separate words, so the `->` you see belongs to the list, never to the returned value.

## Key Rules

1. Draw the pointers on paper before writing any insert or remove.
2. Update the new node's pointers **before** the existing node's pointers.
3. Every operation needs its **empty list** and **single element** cases checked.
4. Keep `head`, `tail` and `size` consistent in one place.
5. Never print a list that might contain a cycle.

## Gotchas Recap

- Forgetting to reset `tail` when a doubly list empties.
- `addLast` on a head-only singly list is O(n); add a `tail` if you need O(1).
- Using `==` instead of `equals` in `contains`.
- Reasoning about `LinkedList` as "faster for inserts": it is only faster if you already hold the node.

## Why This Structure Exists

Linked lists are where pointer discipline is learned. Interview problems (reverse, middle, cycle) all reduce to the three-reference dance above, and the trees and graphs in this folder are the same idea with more than one `next`.
