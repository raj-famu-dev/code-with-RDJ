> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Trie (Prefix Tree)

## Concept

A **trie** stores words as paths: one node per character, starting from an empty root. A flag on a node says "a stored word ends here". Words that share a prefix share the nodes of that prefix, so "does anything start with `ca`?" is a walk of two steps, regardless of how many words are stored.

This version supports lowercase `a` to `z` only, with a fixed `Node[26]` of children, so no `java.util` collection is inside it.

## Big-O (L = length of the word or prefix, n = words, A = alphabet size = 26)

| Operation | Time |
|---|---|
| `insert`, `contains`, `startsWith`, `remove` | **O(L)**, independent of n |
| `countWithPrefix` | **O(L)** (a counter is stored per node) |
| all words with a prefix | O(L + size of that subtree) |
| memory | O(total characters x A) with array children (wasteful); less with a map per node |

Versus a `HashSet<String>`: `contains` is O(L) for both (hashing a string reads all its characters). The trie's real advantage is **prefix queries**: a hash set would scan every word.

## Full Line-by-Line Breakdown

**Node.** `children[26]`, a boolean `isWord`, and `wordsBelow` (how many stored words pass through this node).

**`insert`.** Walk from the root, creating missing child nodes, incrementing `wordsBelow` on the way, and set `isWord` at the end. It first checks `contains` so inserting a duplicate does **not** inflate the counters.

**`contains` vs `startsWith`.** Both walk the path. `contains` additionally requires `isWord`. That flag exists because `ca` is a *path* inside `car` and `cat` without being a stored *word*.

**`remove`.** Decrement `wordsBelow` down the path. The first node whose counter hits 0 is used by no other word, so the whole branch below is cut by setting that child to `null`. If every node on the path is still used by other words, only `isWord` is cleared.

**Autocomplete (`wordsWithPrefix`).** Walk to the prefix node, then collect words depth-first, visiting children `a` to `z`, so results come out **alphabetically** without sorting. The `StringBuilder` is appended to and then un-appended (`deleteCharAt`) as the recursion backtracks.

**`longestPrefixOf(text)`.** Walk the text through the trie and remember the last point at which `isWord` was true.

Real output:

```
size = 7
contains(car) = true, contains(ca) = false (a PATH, not a word), startsWith(ca) = true
insert(car) again returns false, size still 7
autocomplete "car": car, card, care, careful
autocomplete "ca":  car, card, care, careful, cat
autocomplete "do":  dog, dot
autocomplete "x":   (none)
countWithPrefix("car") = 4, countWithPrefix("d") = 2
longestPrefixOf("carefully") = "careful"
remove careful:  "care" still a word = true, careful = false
remove car:      "card" and "care" survive = true, car = false, startsWith(car) = true
remove dog, dot: startsWith(d) = false  (the whole branch was released)
remove(zebra) (absent) returns false, size = 3
IllegalArgumentException: only a-z supported, got 'H' in "Hello"
oracle test: 30000 random operations match java.util.HashSet, prefix counts match a brute-force scan: true (final size 182)
```

**Oracle test.** Random words over a tiny alphabet (`a`, `b`, `c`, length 1 to 5) so prefixes collide constantly. 30,000 random `insert` / `remove` / `contains` calls are compared with `java.util.HashSet` (reference only), and then seven prefixes have their `countWithPrefix` and `wordsWithPrefix(...).length` checked against a **brute-force scan** of the oracle.

## Key Rules

1. A node means "a prefix", the `isWord` flag means "a word". Never confuse the two.
2. Keep per-node counters if you need counts or safe removal.
3. Validate the alphabet at the door; `charAt(i) - 'a'` on a capital letter is an array index out of bounds or a silent wrong slot.
4. Backtrack your `StringBuilder` in recursive collection.
5. Choose the child container by alphabet size: array for small fixed alphabets, map for Unicode.

## Gotchas Recap

- `Node[26]` per node is memory-hungry: 26 references per character stored.
- Case and Unicode are a design decision, not an afterthought.
- Removing only the flag (never cutting branches) works but leaks memory.
- A trie is not automatically better than a hash set; use it when you need prefix operations.

## Why This Structure Exists

The trie shows that the *shape* of a structure can encode the query you want to answer (prefix lookup). It is the foundation for autocomplete, spell checkers and IP routing tables, and it is a good last exercise because it combines arrays, recursion, counters and careful removal.
