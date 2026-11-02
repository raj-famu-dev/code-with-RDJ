# `_6_DunderMethods.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Dunder (double underscore) methods such as `__str__`, `__eq__` and `__len__` are hooks that let your classes plug into Python's syntax and built-in functions: `print(x)`, `a == b`, `len(x)`, `for i in x`, `x[0]`, `a + b`. You never call them directly; Python calls them for you.

They are how Python does what Java does with `toString`, `equals`, `hashCode`, `Comparable`, `Iterable` and (not at all) operator overloading.

## Full Line-by-Line Breakdown

### SECTION 1: __str__ VS __repr__
`__str__` is the friendly text used by `print` and f-strings; `__repr__` is the unambiguous developer text used by the REPL, by containers when they print their contents, and as the fallback if `__str__` is missing. Rule of thumb: always write `__repr__`, add `__str__` only when you want different user-facing text. `!r` in an f-string forces `repr`. The default repr contains a memory address, so the demo prints only its prefix to keep output stable.

Output from a real run:

```text
===== SECTION 1: __str__ VS __repr__ =====
print(m)  -> $19.99
repr(m)   -> Money(1999)
in a list -> [Money(1999), Money(5)] (containers use repr)
f-string  -> $19.99 / Money(1999)
default repr has an address, so only its prefix is shown: <__main__.OnlyDefault object
```

### SECTION 2: __eq__ + __hash__ TRAP
By default `==` compares identity. Defining `__eq__` gives value equality, but Python then sets `__hash__` to `None`, making the class unhashable (unusable in sets or as dict keys). The `P1` case raises `TypeError: unhashable type`. `P2` defines both with the same fields so equal objects share a hash; the set collapses duplicates and the dict lookup with a different-but-equal object works. The rule is the same as Java's `equals`/`hashCode` contract: equal objects must have equal hashes, and the fields used should not change while the object is a key.

Output from a real run:

```text
===== SECTION 2: __eq__ + __hash__ TRAP =====
P1(1) == P1(1): True
Defining __eq__ alone sets __hash__ = None -> unhashable type: 'P1'
P1.__hash__ is None: True
Set of P2(1), P2(1), P2(2) has size: 2
dict lookup with an equal but different object: seven
Hash only works if the fields are not mutated while in a set/dict.
```

### SECTION 3: ORDERING
`sorted` and `max` use `<`. Writing all of `__lt__`, `__le__`, `__gt__`, `__ge__` is tedious, so `@functools.total_ordering` derives the rest from `__eq__` plus ONE of the ordering methods (here `__lt__`). The output shows `<=` and `>` working without being written. Comparing tuples in `__lt__` is a handy trick for multi-field ordering.

Output from a real run:

```text
===== SECTION 3: ORDERING =====
sorted: [v1.9, v2.0, v2.1]
max: v2.1
v1.9 <= v2.0 (derived by total_ordering): True
v2.0 > v1.9 (derived): True
```

### SECTION 4: CONTAINER PROTOCOL
`__len__` powers `len()`, `__getitem__` powers `pl[0]`, `pl[-1]` and slices (the argument may be an int or a `slice`), `__iter__` powers `for` loops and `list()`, and `__contains__` powers `in`. Without `__contains__` and `__iter__`, Python falls back to older behaviours: `OnlyGetItem` is iterable just because it has `__getitem__` raising `IndexError` at the end.

Output from a real run:

```text
===== SECTION 4: CONTAINER PROTOCOL =====
len: 4
pl[0]: a | pl[-1]: d | pl[1:3]: ['b', 'c']
for loop: ['A', 'B', 'C', 'D']
'c' in pl: True
list(pl): ['a', 'b', 'c', 'd']
Iterates with only __getitem__: [0, 10, 20]
```

### SECTION 5: __add__ AND FRIENDS
`a + b` calls `a.__add__(b)`. Returning `NotImplemented` (not raising) tells Python to try the other operand's reflected method and then raise the standard `TypeError` you see in the last line. `3 * v` needs `__rmul__` because `int.__mul__` does not know about `Vec`. `__bool__` customises truthiness; `Vec(0, 0)` is falsy.

Output from a real run:

```text
===== SECTION 5: __add__ AND FRIENDS =====
Vec(1,2) + Vec(3,4) = Vec(4, 6)
Vec(1,2) * 3 = Vec(3, 6)
3 * Vec(1,2) = Vec(3, 6) (needs __rmul__)
bool(Vec(0,0)): False
TypeError: unsupported operand type(s) for +: 'Vec' and 'int'
```

## Key Differences From Java
| Java | Python |
|---|---|
| `toString()` | `__str__` (user text) and `__repr__` (developer text) |
| `equals()` + `hashCode()` | `__eq__` + `__hash__` (defining only `__eq__` makes the class unhashable) |
| `implements Comparable<T>` with `compareTo` | `__lt__` (+ `@total_ordering`), or `key=` in `sorted` |
| `Iterable<T>`/`Iterator<T>` | `__iter__`/`__next__` |
| `size()`, `get(i)` | `__len__`, `__getitem__` |
| No operator overloading (except `+` on String) | Full operator overloading with dunders |
| `Object` methods inherited by name | Any class can opt into protocols by defining dunders |

## Key Rules / Gotchas Recap
- Always define `__repr__`; add `__str__` only if you need a prettier version.
- If you define `__eq__`, define `__hash__` too (or accept unhashable), and base both on the same immutable fields.
- Return `NotImplemented` for unsupported operand types, do not raise.
- `@total_ordering` needs `__eq__` and one ordering method.
- Do not call dunders directly; use `str()`, `len()`, `iter()`, operators.
- Do not make mutable objects hashable by their mutable fields.

## Why This Structure Exists
Every data class in a real project (tensors, requests, records, tokens) depends on these hooks to be printable, comparable, sortable and usable in sets and dicts. The eq/hash trap is a classic cause of de-duplication bugs in data pipelines and security-log analysis.
