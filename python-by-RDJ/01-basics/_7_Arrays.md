# `_7_ListsAndArrays.py`

## Concept
Python's `list` — dynamic-size, mixed-type-capable, and feature-rich enough to replace Java's array/ArrayList distinction entirely, plus slicing and tuples as genuinely new concepts.

## The Full Code

```python
scores = [90, 85, 78, 92, 88]
ages = [21, 25, 19, 34, 40]
fruits = ["Apple", "Banana", "Cherry"]
mixed_list = [1, "two", 3.0, True, None]

print(ages[2])
ages[2] = 20
print(len(ages))
print(ages[-1])

for i in range(len(scores)):
    print(f"Index {i}: {scores[i]}")
for fruit in fruits:
    print(fruit)

fruits.append("Mango")
fruits.insert(1, "Blueberry")
fruits.remove("Banana")
popped = fruits.pop()
popped_at_index = fruits.pop(0)
del fruits[0]

print(sum(scores))
print(sum(scores) / len(scores))
print(max(scores))
print(min(scores))
print(sorted(scores))
scores.sort()
scores.sort(reverse=True)

numbers_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(numbers_list[2:5])
print(numbers_list[:3])
print(numbers_list[7:])
print(numbers_list[::2])
print(numbers_list[::-1])

grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(grid[1][2])
for row in grid:
    for value in row:
        print(value, end=" ")
    print()

flexible_list = []
flexible_list.append(10)

original = [1, 2, 3]
wrong_copy = original
wrong_copy[0] = 999
real_copy_1 = original.copy()
real_copy_2 = original[:]
real_copy_3 = list(original)

coordinates = (10, 20)

squares = [x ** 2 for x in range(1, 6)]
even_numbers = [x for x in range(1, 20) if x % 2 == 0]
```

## Line-by-Line Breakdown

### `scores = [90, 85, 78, 92, 88]`
Declared with square brackets, no size specified anywhere — Python lists are dynamic by default. No `new int[5]` equivalent exists at all for a "fixed" version used in everyday code.

### `mixed_list = [1, "two", 3.0, True, None]`
Lists can hold **mixed types** in one collection — an `int`, a `str`, a `float`, a `bool`, and `None` all together, freely. Java arrays require a single declared type; achieving this in Java would need `Object[]` plus constant casting.

### `ages[-1]`
**Negative indexing** — a Python-only feature with no Java equivalent at all. `-1` refers to the last element, `-2` the second-to-last, and so on, without needing `ages[len(ages) - 1]`.

### `len(ages)`
`len()` is a **function**, not a property — replaces Java's `.length`.

### `.append()`, `.insert()`, `.remove()`, `.pop()`, `del`
These five operations are what make lists genuinely dynamic: `.append()` adds to the end, `.insert(index, value)` adds at a specific position (shifting others right), `.remove(value)` deletes by **value** (first match, not index), `.pop()` removes and returns the last element (or a specified index), and `del list[index]` deletes by index without returning anything. **None of this is possible with a Java array at all** — Java would require creating an entirely new array to simulate any of these operations.

### `sum(scores)`, `max(scores)`, `min(scores)`, `sorted(scores)`
Built-in functions handling what Java requires manual loops to accomplish. `sorted()` returns a **new** sorted list, leaving the original untouched; `.sort()` instead sorts the original list **in place**.

### `numbers_list[2:5]`
**Slicing** — one of Python's signature features, with genuinely no Java equivalent. `[2:5]` extracts indices 2, 3, 4 (end exclusive, same rule as `range()`). `[:3]` means "from the start." `[7:]` means "to the end." `[::2]` means "every 2nd element." `[::-1]` **reverses the entire list** in one expression — Java needs a full loop or `Collections.reverse()` to accomplish the same thing.

### `grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]`
A 2D structure built simply as a list containing other lists — no special `[][]` declaration syntax needed. Access and nested looping work the same way conceptually as Java's 2D arrays.

### `wrong_copy = original` → modifying `wrong_copy` also changes `original`
**The exact same reference-copy gotcha as Java arrays.** Simple assignment makes `wrong_copy` point to the *same* list object in memory as `original` — it is not a real copy. `.copy()`, slicing with `[:]`, and the `list()` constructor are the three standard ways to create a genuinely independent copy.

### `coordinates = (10, 20)`
A **tuple** — written with parentheses instead of brackets. Once created, it can never be modified (`coordinates[0] = 99` crashes with a `TypeError`). This is Python's closest conceptual equivalent to an immutable, "locked" collection — there's no direct Java equivalent, though it shares some spirit with `final`.

### `squares = [x ** 2 for x in range(1, 6)]`
A **list comprehension** — builds an entire new list in one line, based on a loop (and optionally a filtering condition, as in `even_numbers`). This replaces what Java needs a full loop with repeated `.add()` calls on an `ArrayList` to accomplish.

## Key Differences From Java

| Concept | Java | Python |
|---|---|---|
| Size | Fixed at creation | Fully dynamic |
| Mixed types | Not allowed without `Object[]` + casting | Fully allowed in one list |
| Getting length | `.length` (property) | `len(list)` (function) |
| Negative indexing | Doesn't exist | `list[-1]` gets the last element |
| Adding/removing elements | Must create a new array | `.append()`, `.insert()`, `.remove()`, `.pop()`, `del` |
| Sum/average/max/min | Manual loops | Built-in `sum()`, `max()`, `min()` |
| Out-of-bounds error | `ArrayIndexOutOfBoundsException` | `IndexError` |
| Slicing | Doesn't exist | `list[start:stop:step]` |
| Reversing | `Collections.reverse()` or manual loop | `list[::-1]` |
| Fixed-size equivalent | Array is the default | Tuple — immutable, used for a different purpose |
| Building a filtered/transformed list | Loop + `.add()` | List comprehension |

## Key Rules / Gotchas Recap

- Simple assignment (`b = a`) copies the reference, not the contents — identical pitfall to Java arrays, requiring `.copy()`, `[:]`, or `list()` for a true copy
- Slicing's end index is exclusive, same convention as `range()`
- There is no Java-style choice between a fixed array and a dynamic ArrayList — Python's `list` is simply the universal default for both roles

## Why This Structure Exists

In Java, choosing between `array` (fixed, low-level) and `ArrayList` (dynamic, feature-rich) is a real decision based on performance and flexibility needs. Python removes that decision entirely — `list` already behaves like Java's `ArrayList` by default, and the closest thing to Java's rigid, unchangeable array is actually the **tuple**, reached for specifically when immutability — not performance — is the goal.