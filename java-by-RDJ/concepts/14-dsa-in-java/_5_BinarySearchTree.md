> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Binary Search Tree

## Concept

A **binary search tree** keeps one rule at every node: everything in the **left** subtree is smaller, everything in the **right** subtree is larger. Searching then discards a whole subtree per step, like binary search on a sorted array, but inserts and removals do not need to shift anything.

## Big-O (h = height, n = nodes)

| Operation | Time |
|---|---|
| `insert`, `contains`, `remove`, `min`, `max` | **O(h)** |
| any traversal (in / pre / post / level order) | **O(n)** |
| **balanced** tree | h = O(log n), so the first row is **O(log n)** |
| **degenerate** tree (keys inserted already sorted) | h = n, so the first row is **O(n)** |

This tree does **not** rebalance itself. AVL and red-black trees (the one inside `TreeMap`/`TreeSet`) add rotations to *guarantee* O(log n). Those are the next step, not covered here.

## Full Line-by-Line Breakdown

**`insert` / `contains`.** Start at the root and go left if `key < node.key`, right otherwise, until you find the key or fall off the tree. Duplicates are ignored (set behaviour).

**`remove` (the three cases).**
1. **Leaf**: unlink it.
2. **One child**: replace the node with that child.
3. **Two children**: copy the node's **in-order successor** (the smallest key in its right subtree) into it, then delete the successor from the right subtree. The successor has no left child, so that second delete is case 1 or 2.

**Traversals.** *In-order* (left, node, right) visits keys in **sorted order**, which is the property that makes a BST a sorted structure. *Pre-order* (node first) is how you copy a tree; *post-order* (node last) is how you delete one; *level-order* uses a queue (a plain array here) and visits by depth.

**`isValid`.** Pass an allowed `(low, high)` range down the tree and require every key to stay inside it. The tempting version that only compares each node with its **direct** children is wrong, because a node deep in the left subtree can still be larger than the root.

Real output:

```
size = 8, height = 4, min = 20, max = 80
in-order    (sorted):    20 30 35 40 50 60 70 80
pre-order   (node first): 50 30 20 40 35 70 60 80
post-order  (node last):  20 35 40 30 60 80 70 50
level-order (by depth):   50 30 70 20 40 60 80 35
contains(60) = true, contains(65) = false
insert(50) again returns false (duplicate ignored), size 8
remove leaf 20:        50 30 70 40 60 80 35
remove one-child 30:   50 40 70 35 60 80
remove two-child 50:   60 40 70 35 80   (60 replaced it)
still valid BST: true, in-order still sorted: 35 40 60 70 80
remove(999) (absent) returns false
1000 keys inserted SORTED:   height = 1000   (a linked list in disguise: O(n))
1000 keys inserted SHUFFLED: height = 24   (a perfect tree would be 10; random insertion order is only ROUGHLY balanced, here about 2.4x that)
oracle test: 30000 random operations match java.util.TreeSet, tree still valid: true (final size 261)
```

**The numbers worth remembering.** Same 1000 keys: inserted in sorted order the height is **1000** (every lookup walks the whole chain), inserted in a shuffled order it is **24**. A perfectly balanced tree would be 10. This is the entire argument for self-balancing trees, in one run. (The shuffle uses a fixed seed, so 24 is reproducible, but it is one shuffle, not a statistical claim about random BSTs.)

**Oracle test.** 30,000 random `insert` / `remove` / `contains` calls against `java.util.TreeSet` (reference only), checking return values and size each step, then the final in-order sequence and `isValid()`.

## Key Rules

1. In-order traversal of a valid BST is sorted. Use that to test yours.
2. Check the **range**, not just the children, when validating.
3. Removal with two children uses the in-order successor (or predecessor).
4. Without balancing, input order decides performance.
5. Recursion depth equals tree height; a degenerate tree can overflow the stack.

## Gotchas Recap

- Forgetting the single-child cases and handling only "leaf" and "two children".
- Decrementing `size` in the wrong recursion frame (here the two-child case lets the recursive call on the successor do the decrement).
- Using `==` to compare boxed keys in a generic version.
- Assuming "tree" means "log n". It means "height", which you must manage.

## Why This Structure Exists

The BST is the bridge from lists to ordered maps and from loops to recursion. It also sets up the heap (a tree in an array), the trie (a tree of characters) and graph traversal (a tree with cycles allowed).
