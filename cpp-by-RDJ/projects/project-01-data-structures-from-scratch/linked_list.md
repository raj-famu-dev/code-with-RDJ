# `linked_list.hpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`LinkedList<T>` stores each element in its own heap node with `prev` and `next` pointers, like `std::list` and Java's `LinkedList`. Inserting or erasing at a known position only rewires pointers, so it is O(1) and never moves an element, but reaching the i-th element means walking i links and every node is a separate allocation.

## Full Line-by-Line Breakdown

### Node and the two ends
`Node` holds the value and two pointers. The list keeps `head_`, `tail_` and `size_`. `nullptr` marks "no neighbour", and an iterator holding `nullptr` is `end()`. A node constructor forwards its arguments to `T`, so `emplace_back(args...)` builds the element directly inside the node.

### Push, pop and the `new` trap
`emplace_back` does `new Node(...)`. If `T`'s constructor throws, the `new` expression frees the raw memory itself and nothing was linked yet, so the list stays valid. Only after the node exists are `tail_`, `head_` and `size_` updated. `pop_front` and `pop_back` call `unlink`, which patches the neighbours (or head/tail) and deletes the node.

### `clear()` and the dangling `next`
```text
Node* next = n->next;   // save BEFORE deleting
delete n;
n = next;
```
Reading `n->next` after `delete n` would be a use-after-free. Cleanup is a loop, not recursion, so a very long list cannot overflow the stack.

### Iterators (bidirectional)
One template `Iter<bool Const>` makes both `iterator` and `const_iterator`. A constrained converting constructor allows `iterator -> const_iterator` but never the reverse. `--end()` is special: a null node means "past the end", so decrement jumps to `tail_` (the iterator remembers its list for exactly this reason). `insert(pos, v)` inserts *before* `pos`; `erase(pos)` returns the iterator to the next element. Neither invalidates other iterators.

### `reverse()`
Swap `prev` and `next` in every node, then swap `head_` and `tail_`. The walk uses `n = n->prev` *after* the swap, because the old `next` is now stored in `prev`. No element is copied or moved. The demo output (Section 2) shows it:

```text
===== SECTION 2: insert 1000 items at the FRONT (array shifts, list relinks) =====
DynamicArray: element moves=501520 (each insert shifts the whole tail; n(n-1)/2 = 499500 shifts for n=1000, plus relocation moves)
LinkedList:   element copies=0 moves=1000 (nodes are linked, elements never shift)
after insert(99 before 3) and reverse(): 5 4 3 99 2 1
```

`LinkedList: element copies=0 moves=1000` means 1000 front insertions never shifted a single element; the array version needed hundreds of thousands of moves for the same job. (Those numbers are exact counts from this run, not timings.)

### Rule of five
Copy builds a new list by pushing each value; move steals head, tail and size; both assignments use copy/move-and-swap; the destructor is `clear()`.

## Key Differences From Java
| Java `LinkedList<E>` | C++ `LinkedList<T>` |
|---|---|
| Nodes are collected by the garbage collector | Each node needs `delete`; forgetting it leaks, doing it twice is a double free |
| `ListIterator` with `hasNext()/next()` | Iterator is a small object with `*`, `++`, `--`, compared with `==` |
| Holds references; copying the list shares elements | Holds values; the copy constructor deep-copies every element |
| `remove()` while iterating throws `ConcurrentModificationException` | Erasing through `erase(pos)` is fine; using an erased iterator is undefined behaviour |

## Key Rules / Gotchas Recap
- Save `next` before deleting a node.
- `end()` is a null node; `--end()` must find the tail.
- Insert-before semantics: `insert(end(), v)` appends.
- In practice a vector beats a linked list for most work (cache locality); a list wins only when you need stable iterators and cheap splicing.

## Why This Structure Exists
Pointer-linked nodes are the basis of allocators' free lists, LRU caches, task queues and kernel structures, and pointer rewiring mistakes in exactly this kind of code are the origin of many real use-after-free and double-free vulnerabilities (see project 02).
