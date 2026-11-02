> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Min-Heap (Priority Queue)

## Concept

A **min-heap** always lets you take the smallest element first, in O(log n), without keeping everything sorted. It is a **complete binary tree stored in a plain array**:

```
parent of i  = (i - 1) / 2
left child   = 2i + 1
right child  = 2i + 2
```

One rule: **every parent is <= its children.** That puts the minimum at index 0. It says nothing about left versus right, so a heap is *not* sorted and cannot be searched quickly.

## Big-O (n = elements)

| Operation | Time |
|---|---|
| `peek` (minimum) | **O(1)** |
| `add` | **O(log n)** (append, then sift up) |
| `poll` (remove minimum) | **O(log n)** (move last to root, then sift down) |
| build from n values (`heapify`) | **O(n)** |
| `contains`, remove an arbitrary element | **O(n)** |
| heap sort | **O(n log n)** time, **O(1)** extra space |
| top-k largest with a size-k heap | **O(n log k)** time, **O(k)** space |

## Full Line-by-Line Breakdown

**`add`.** Put the value in the next free slot (keeps the tree complete), then **sift up**: while the parent is larger, swap with it.

**`poll`.** Save `data[0]`, move the **last** element to the root (keeps the tree complete), then **sift down**: swap with the **smaller** child until neither child is smaller. Choosing the smaller child is what preserves the rule; picking the larger one breaks it.

**`heapify`.** Instead of adding n times, copy the array and sift down every **non-leaf** node from `size/2 - 1` back to 0. Leaves are already valid heaps. Real measurement from the run:

```
build from 100000 random values: repeated add = 128055 swaps, heapify = 74453 swaps (both valid: true)
```

Repeated `add` is O(n log n) in the worst case, but with random input most elements barely move, so the measured gap here is **1.7x** and not the log factor. The O(n) bound for `heapify` is a proof about the worst case (most nodes are near the bottom and sift only a level or two). One run on random data is an illustration, not the proof.

**Heap sort.** Build a *max*-heap in place, then repeatedly swap the maximum to the end and sift the shrinking heap. No extra array.

**Top-k.** To keep the **k largest** values from a stream, hold a **min**-heap of size k. Its root is the weakest of the current best k; a new value replaces it only if bigger. That is the counter-intuitive part: you use a *min*-heap to track the *largest*.

Real output:

```
array layout after adding 5 3 8 1 9 2: [1 3 2 5 9 8]   (index 0 is the minimum, NOT a sorted array)
peek = 1, size = 6
polling everything gives sorted order: 1 2 3 5 8 9
NoSuchElementException: heap is empty
heap sort: 0 1 2 3 4 5 6 7 8 9
top 3 largest of 15 3 99 42 8 77 61 5 23 90: 77 90 99
oracle test: 50000 random operations match java.util.PriorityQueue: true
```

**Oracle test.** 50,000 random `add` / `poll` operations against `java.util.PriorityQueue` (reference only). Every polled value, every `peek`, and the size must match, and `isValidHeap()` must hold at the end.

## Key Rules

1. Array indices instead of node objects: no pointers, good cache behaviour.
2. Sift **up** after adding, sift **down** after removing.
3. Sift down towards the **smaller** child (min-heap).
4. Heaps answer "what is next?" not "is X in here?".
5. For top-k, a min-heap of size k, not a max-heap of size n.

## Gotchas Recap

- `PriorityQueue` iteration and `toString` are **not** in sorted order (just like `layout()` above).
- It is not stable: equal priorities come out in no guaranteed order.
- Changing an element's priority after insertion needs a remove (O(n)) and re-add, or an indexed heap.
- Off-by-one in the child formulas is the usual bug: 0-based uses `2i + 1`, 1-based uses `2i`.

## Why This Structure Exists

Priority queues are everywhere: schedulers, Dijkstra's shortest path, "k largest", merging sorted streams. Building the heap yourself shows why `poll` is O(log n) and makes the `heapify` O(n) interview question something you can reason about instead of recite.
