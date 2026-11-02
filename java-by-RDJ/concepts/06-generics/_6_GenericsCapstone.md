> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Generics Capstone: Stack<T> and Queue<T>

## Concept

Build your own generic `Stack<T>` (last in, first out) and `Queue<T>` (first in, first out) on a chain of linked nodes, with no `java.util` collections inside. It pulls together generic classes, generic nested types, bounds and PECS wildcards.

## Full Line-by-Line Breakdown

**`Node<T>`.** A private nested generic class: `value` and a `next` pointer.

**`Stack<T>`.** `push` puts a node at the head; `pop`/`peek` read the head and throw `NoSuchElementException` when empty. It implements `Iterable<T>` through an anonymous `Iterator<T>`, so `for (T item : stack)` works.

**`Queue<T>`.** Keeps a `head` **and** a `tail`: `enqueue` adds at the tail, `dequeue` removes from the head. When the last element is removed the tail must be reset to `null` too (a classic bug); the demo re-uses the queue after emptying it to prove it works.

**PECS in `Stack`.**
- `pushAll(Collection<? extends T>)`: reads from a producer.
- `popAllInto(Collection<? super T>)`: writes into a consumer.

A `Stack<Number>` can take a `List<Integer>` and a `List<Double>`, then empty into a `List<Object>`.

**`largest(Iterable<T>)`** with `<T extends Comparable<? super T>>` works on both the `Queue<String>` and `Stack<Integer>`.

**`isBalanced(String)`** is a real use of a stack: push openers, pop and match closers.

**Output:**

```
Stack(top -> bottom)[c b a], size 3
pop  = c
peek = b
Queue(head -> tail)[1 2 3], size 3
dequeue = 1
peek    = 2
emptied: isEmpty = true
after re-use: Queue(head -> tail)[99]
pop on empty: stack is empty
Stack(top -> bottom)[1.5 0.5 3 2 1]
popped everything into List<Object>: [1.5, 0.5, 3, 2, 1]
largest word  = zebra
largest number = 42
isBalanced("([]{})") = true
isBalanced("(]") = false
isBalanced("((") = false
isBalanced("") = true
```

## Key Rules

1. Reset `tail` to `null` when a queue becomes empty.
2. Read from `? extends T`, write into `? super T`.
3. Implement `Iterable<T>` to get the for-each loop.
4. Throw a clear exception on empty `pop`/`dequeue` instead of returning `null`.

## Gotchas Recap

- Forgetting `tail = null` leaves a dangling reference and breaks the next `enqueue`.
- The nested `Stack` and `Queue` share names with `java.util.Stack` and `java.util.Queue`. Inside this file the nested ones win, which is confusing: in real code, pick different names.
- This is a teaching structure, not thread-safe (see `05`).

## Why This Structure Exists

Both structures reuse the same `Node<T>`, so you can compare how one idea (a chain) gives two different behaviours, and the bracket checker shows why anyone wants a stack.
