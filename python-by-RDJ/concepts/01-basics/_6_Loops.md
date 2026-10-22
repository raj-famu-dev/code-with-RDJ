# `_6_Loops.py`

## Concept
`for` and `while` loops — with no C-style counting loop and no `do-while` at all, plus `enumerate()`, `for...else`, and the complete absence of labeled breaks.

## The Full Code

```python
for i in range(1, 6):
    print("For loop iteration:", i)

for i in range(5):
    print("range(5) gives:", i)

for i in range(0, 10, 2):
    print("Even number:", i)

count = 1
while count <= 5:
    print("While loop count:", count)
    count += 1

attempts = 10
while True:
    print("Simulating do-while, attempts =", attempts)
    attempts += 1
    if attempts >= 15:
        break

print("Multiplication table (nested loop):")
for row in range(1, 4):
    for col in range(1, 4):
        print(row, "x", col, "=", row * col)

for i in range(1, 11):
    if i == 6:
        break
    print("break demo, i =", i)

for i in range(1, 11):
    if i % 2 == 0:
        continue
    print("continue demo, odd number:", i)

numbers = [10, 20, 30, 40, 50]
for num in numbers:
    print("For-each value:", num)

for letter in "Python":
    print("Letter:", letter)

names = ["Alice", "Bob", "Charlie"]
for index, value in enumerate(names):
    print(f"Index {index}: {value}")

found = False
for i in range(1, 4):
    for j in range(1, 4):
        if i == 2 and j == 2:
            found = True
            break
    if found:
        break
    print(f"i={i}, j={j}")

def find_pair():
    for i in range(1, 4):
        for j in range(1, 4):
            if i == 2 and j == 2:
                return i, j
    return None

for i in range(1, 6):
    if i == 10:
        break
    print("Searching...", i)
else:
    print("Loop completed without breaking - else block runs!")
```

## Line-by-Line Breakdown

### `for i in range(1, 6):`
Python's `for` loop **always** iterates over a sequence — there is no C-style `for(int i=0; i<5; i++)` syntax at all. `range(1, 6)` generates the counting sequence itself: start at `1` (inclusive), stop before `6` (exclusive), producing `1, 2, 3, 4, 5`.

### `for i in range(5):`
A single-argument `range()` assumes a start of `0`, producing `0, 1, 2, 3, 4`.

### `for i in range(0, 10, 2):`
A third argument to `range()` sets the step size — here, every 2nd number: `0, 2, 4, 6, 8`.

### `while count <= 5: ... count += 1`
Behaves identically to Java's `while` loop — condition checked before each iteration. Note `count += 1`, not `count++` — recap from Topic 3, increment operators don't exist in Python at all.

### `while True: ... if attempts >= 15: break`
**Python has no `do-while` loop whatsoever** — this is the standard workaround, achieving the same "runs at least once" effect by using an infinite `while True:` loop with a manual `break` condition inside it.

### The nested multiplication-table loop
Nesting works through indentation levels, same mechanism as nested `if` statements from Topic 5 — no braces to count.

### `break` and `continue`
Identical keywords, identical behavior to Java — `break` exits the loop entirely, `continue` skips only the current iteration.

### `for num in numbers:` / `for letter in "Python":`
Every Python `for` loop is fundamentally a **for-each** loop — there's no separate "enhanced for" syntax the way Java distinguishes it, since this is simply the only style `for` has. Notably, **strings are directly iterable** — looping over individual characters needs no special method at all, unlike Java requiring `.toCharArray()` first.

### `for index, value in enumerate(names):`
A plain for-each loop only gives you the **value**, never the index. `enumerate()` wraps a sequence to provide both the index and the value together in each iteration — this is what replaces Java's indexed `for(int i=0; i<arr.length; i++)` pattern whenever you specifically need the position.

### The `found` flag workaround
Python has **no labeled break** — Java's `break outerLoop;` has no direct equivalent at all. The standard workaround shown here uses a manual boolean flag: set it when the target condition is found, `break` the inner loop, then check the flag immediately after to also `break` the outer loop.

### `def find_pair(): ... return i, j`
A cleaner alternative to the flag-variable workaround, when applicable: wrapping the nested loops inside a function lets `return` exit **both** loops instantly, from any depth, in one line.

### `for i in range(1, 6): ... else: print(...)`
**`for...else` is a genuine Python-only feature with no Java equivalent at all.** The `else` block runs **only if the loop completes without ever hitting a `break`**. If a `break` does occur partway through, the `else` block is skipped entirely — this is useful for "search and report if nothing was found" patterns without needing a separate flag variable.

## Key Differences From Java

| Concept | Java | Python |
|---|---|---|
| Counting loop | `for(int i=0; i<5; i++)` | `for i in range(5):` |
| For-each loop | Separate "enhanced for" syntax | **The only** for-loop style that exists |
| do-while | Built-in keyword | **Doesn't exist** — simulate with `while True:` + `break` |
| Getting index during iteration | Natural with indexed for loop | Needs `enumerate()` |
| Labeled break | `break outerLoop;` | **Doesn't exist** — use a flag variable or a function with `return` |
| Iterating a String directly | Requires `.toCharArray()` first | Fully supported, no conversion needed |
| `for...else` / `while...else` | No equivalent at all | Runs `else` only if the loop completes without a `break` |

## Key Rules / Gotchas Recap

- `range(start, stop)` is exclusive on the stop end — `range(1, 6)` produces `1` through `5`, not through `6`
- Forgetting to update a `while` loop's condition variable causes an infinite loop, exactly as in Java
- Labeled break is a genuine capability gap, not just a syntax difference — you must consciously restructure logic to replicate what Java does in one line

## Why This Structure Exists

Loops process collections, repeat calculations, and wait for conditions to change — Python consolidates this down to just two loop keywords (`for` and `while`) by making `for` universally sequence-based, which is simpler to reason about but requires `range()`, `enumerate()`, and workaround patterns to recover some of the flexibility Java's more varied loop syntax provides natively.