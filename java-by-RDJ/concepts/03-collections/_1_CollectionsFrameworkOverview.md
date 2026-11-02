# `_1_CollectionsFrameworkOverview.java`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The Collections Framework is a family of interfaces (`List`, `Set`, `Queue`, `Deque`, `Map`) plus classes that implement them. The interface says **what** you can do; the class decides **how** the data is stored and how fast each operation is.

## Full Line-by-Line Breakdown

### SECTION 1: The hierarchy
`Iterable` → `Collection` → `List` / `Set` / `Queue` (→ `Deque`). `Map` is a **separate tree**.
```java
System.out.println("A List is a Collection: " + (new ArrayList<String>() instanceof Collection));
```
Three `instanceof` checks print `true` for `ArrayList`, `HashSet`, and `ArrayDeque`, proving all three are `Collection`s. `Iterable<String> asIterable = asCollection;` shows every `Collection` is also `Iterable`, which is why for-each works on all of them.

### SECTION 2: Why `Map` is not a `Collection`
`Collection` is built around adding and removing **one** element. A `Map` stores **pairs** (`put(key, value)`), so a single-element `add` makes no sense. The commented-out `Collection<?> c = ages;` would be a compile error. Instead a `Map` gives you three Collection **views**: `keySet()`, `values()`, `entrySet()`. Output: `Keys view: [Ana], values view: [20]`.

### SECTION 3: Program to the interface
```java
List<String> names = new ArrayList<>();
```
The variable is typed `List`, the class is chosen at `new`. Switching to another `List` implementation later is a one-word change. Output shows a `List` keeps order and duplicates: `[Zed, Amy, Zed]`.

### SECTION 4: Four shapes, same input
- `TreeSet` of the names: `[Amy, Zed]` (unique, sorted)
- `ArrayDeque.poll()` returns `Zed` (FIFO: first in, first out)
- `TreeMap` with `merge(n, 1, Integer::sum)`: `{Amy=1, Zed=2}` (key → count)

### SECTION 5: Methods that live on `Collection`
`size()`, `contains()`, `isEmpty()`, `remove()` work on any `List`, `Set`, or `Queue`. `c.remove("Zed")` removes only the **first** match in a list, so one `Zed` is left: `[Amy, Zed]`. The for-each over `asIterable` prints nothing because `asCollection` is a separate, empty list.

### SECTION 6: Picking a type
Order and index access → `List`; uniqueness → `Set`; processing in turn → `Queue`/`Deque`; lookup by key → `Map`. The two commented-out lines would not compile: `ArrayList` is not a `Set`, and `HashMap` is not a `Collection`.

## Key Rules / Gotchas Recap
- `Map` is **not** a `Collection`, but it exposes Collection views
- Declare variables with the interface type; choose the class at `new`
- `remove(Object)` on a list removes only the first match

## Why This Structure Exists
Almost every real program stores groups of things. Knowing the four shapes (ordered list, unique set, waiting line, key lookup) lets you pick the right one **before** you write code, instead of forcing everything into an `ArrayList`. The next files go through each class in detail.
