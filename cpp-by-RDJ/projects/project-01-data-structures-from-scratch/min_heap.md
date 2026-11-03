# `min_heap.hpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`MinHeap<T, Less>` is a binary heap stored in a plain array: the smallest element is always at index 0, and every parent is no larger than its children. That makes `top()` O(1) and `push`/`pop` O(log n), which is what a priority queue (a scheduler, Dijkstra's algorithm, "top-k" selection) needs. The array underneath is our own `DynamicArray`, so the heap uses no standard container either.

## Full Line-by-Line Breakdown

### Index arithmetic
For index `i`: parent `(i - 1) / 2`, children `2i + 1` and `2i + 2`. No pointers are stored; the tree shape is implied by the positions.

### `push` and `sift_up`
Append at the end (the next free leaf), then swap with the parent while the new element is "less" than its parent. At most one swap per tree level, so O(log n).

### `pop` and `sift_down`
Take the root, move the last element into the root slot, shrink the array, then `sift_down`: swap with the *smaller* of the two children until neither child is smaller. Choosing the smaller child is what keeps the heap property for the other child.

### Heapify (`build`)
Constructing from n items does not need n pushes. Leaves are already valid one-element heaps, so `build` sifts down only indices `n/2 - 1` down to 0: O(n). The demo counts comparisons with an instrumented comparator:

```text
===== SECTION 4: MinHeap (binary heap in an array) =====
12 seeded random ints popped in order: 13 14 14 20 24 26 35 42 50 67 76 78 
n=1000: comparisons for 1000 pushes=2222, for 1000 pops=14971 (reference n*log2(n)=9966)
heapify of the same 1000 items: comparisons=1869 (heapify is O(n); compare with the push count above)
```

(`reference n*log2(n)` is just the formula value for orientation, not a claim about the heap; the other numbers are exact counts from this run.) Heapify used fewer comparisons than 1000 pushes here, and popping everything (heap sort) used about 15 comparisons per element.

### The `Less` parameter: a convention to remember
`Less(a, b)` true means "a belongs nearer the top". With the default `std::less<T>` the smallest is on top. With `std::greater<T>` you get a max-heap. **This is the opposite of `std::priority_queue`**, whose default `std::less` puts the LARGEST on top; the tests compare against `std::priority_queue<int, vector<int>, greater<int>>` for that reason. `Less` can also be a lambda wrapped in `std::function`.

## Key Differences From Java
| Java `PriorityQueue<E>` | C++ `MinHeap<T, Less>` |
|---|---|
| Min-heap by default, natural ordering or a `Comparator` | Min-heap by default with `std::less`; ordering is a template argument |
| `poll()` returns the head or null | `pop()` returns the value and throws `std::out_of_range` when empty |
| `new PriorityQueue<>(collection)` heapifies | `MinHeap(DynamicArray<T>)` or an initializer list heapifies in O(n) |
| `std::priority_queue` has no Java twin quirk | `std::priority_queue` is a MAX-heap by default: the opposite convention |

## Key Rules / Gotchas Recap
- Pop from an empty heap is an error: check `empty()` or catch the exception.
- Duplicates are fine; the pop order among equal elements is unspecified.
- Heapify is O(n); n pushes are O(n log n).
- A heap is not sorted, only partially ordered; popping everything yields sorted order (heap sort).

## Why This Structure Exists
Priority queues schedule work (thread pools, event loops), drive graph and search algorithms, and keep the best k candidates in ranking and retrieval systems, so knowing exactly what `push` and `pop` cost and why is basic systems literacy.
