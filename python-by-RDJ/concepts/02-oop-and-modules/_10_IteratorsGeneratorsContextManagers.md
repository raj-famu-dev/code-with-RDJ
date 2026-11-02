# `_10_IteratorsGeneratorsContextManagers.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
An iterator is any object you can ask for the next value until it says it is finished; a generator is the easy way to write one using `yield`, producing values lazily one at a time instead of building a whole list. A context manager guarantees setup and cleanup around a block using `with`, even when an exception occurs.

Together they let you process large or infinite data with tiny memory and manage files, connections and locks safely.

## Full Line-by-Line Breakdown

### SECTION 1: THE ITERATOR PROTOCOL
`iter(x)` returns an iterator and `next()` yields values until `StopIteration`. A `for` loop is exactly that: call `iter()` once, call `next()` repeatedly, stop on `StopIteration`. `Countdown` implements `__iter__` (returning itself) and `__next__`. Because it is its own iterator it is exhausted after one pass, so the second `list(cd)` is empty. A container such as a list returns a fresh iterator each time, which is why lists can be looped many times.

Output from a real run:

```text
===== SECTION 1: THE ITERATOR PROTOCOL =====
next: 10 20
StopIteration signals the end
A for loop = iter() once, then next() until StopIteration.
first pass: [3, 2, 1]
second pass (exhausted!): []
```

### SECTION 2: GENERATORS
A function containing `yield` returns a generator object when called, and none of its code runs yet. The first `next()` runs it up to the first `yield`; it pauses there with all local variables kept, and resumes on the next call. `list(g)` gets the rest, and a finished generator is empty. `fib()` is an infinite sequence that is safe because values are produced on demand. `yield from` delegates to another iterable. A `return` value inside a generator ends it (it becomes the `StopIteration` value and is not part of the output).

Output from a real run:

```text
===== SECTION 2: GENERATORS =====
created generator, nothing ran yet: generator
  (generator body starts only on first next)
next: 3
rest: [2, 1]
exhausted: []
first 10 Fibonacci: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
yield from: [1, 2, 3]
```

### SECTION 3: GENERATOR EXPRESSIONS
`(n * n for n in ...)` is like a list comprehension with round brackets and no list built in memory. `sum` consumes it value by value. The size comparison is a measurement from this interpreter and only the comparison is claimed. `any(n > 5 for n in range(10**9))` stops at the first true value, so it finishes immediately instead of looping a billion times.

Output from a real run:

```text
===== SECTION 3: GENERATOR EXPRESSIONS =====
sum via list: 332833500 | via generator: 332833500
sys.getsizeof list > generator: True (sizes are a measurement of this interpreter; exact bytes not claimed)
any() short-circuits: True
```

### SECTION 4: TRAP - ONE-SHOT
A generator can only be consumed once. The second `list(evens)` is silently empty, with no error. If you need to loop twice, store the values in a list/tuple or create a new generator by calling the function again.

Output from a real run:

```text
===== SECTION 4: TRAP - ONE-SHOT =====
first use: [0, 2, 4, 6, 8]
second use: [] <- silently empty!
Fix: store a list, or call the generator function again.
```

### SECTION 5: CLASS-BASED CONTEXT MANAGER
`with Resource("db") as r:` calls `__enter__` (its return value becomes `r`) and always calls `__exit__` on the way out, even after an exception. `__exit__` receives the exception type, value and traceback (all `None` when there was no error). Returning `True` swallows the exception (done for `ValueError`); returning a false value lets it continue (`KeyError` still propagates, yet "close db3" printed first).

Output from a real run:

```text
===== SECTION 5: CLASS-BASED CONTEXT MANAGER =====
  open db
  using db
  close db (exception: None)
  open db2
  close db2 (exception: ValueError)
execution continued after the with block
  open db3
  close db3 (exception: KeyError)
KeyError propagated, but cleanup still ran
```

### SECTION 6: @contextmanager
`contextlib.contextmanager` turns a generator with ONE `yield` into a context manager: code before `yield` is setup, the yielded value is the `as` target, code after is teardown. Wrap the `yield` in `try/finally`, otherwise teardown is skipped when the body raises. `contextlib.suppress` is a ready-made manager that ignores chosen exceptions.

Output from a real run:

```text
===== SECTION 6: @contextmanager =====
  setup conn
  got CONN
  teardown conn
  setup conn2
  teardown conn2
teardown ran despite the error
contextlib.suppress ignored ZeroDivisionError
```

### SECTION 7: with AND FILES
A file opened in `with` is closed when the block ends (`f.closed` is `True`). A file opened manually stays open until you remember to call `close()`; forgetting leaks file handles and can lose buffered writes. A temporary directory keeps the demo clean.

Output from a real run:

```text
===== SECTION 7: with AND FILES =====
closed after with: True
manual open without with, closed? False
```

## Key Differences From Java
| Java | Python |
|---|---|
| `Iterator<T>`: `hasNext()` + `next()` | `__next__` raising `StopIteration`; no `hasNext` |
| Streams (`stream().map().filter()`) lazy pipelines | Generators and generator expressions; much lighter syntax |
| Writing an `Iterator` takes an inner class | A function with `yield` |
| try-with-resources (`AutoCloseable.close()`) | `with` + `__enter__`/`__exit__` |
| `close()` cannot swallow exceptions by itself | `__exit__` can suppress exceptions by returning `True` |
| A Stream can be consumed only once (`IllegalStateException`) | A generator is exhausted silently, with no exception |
| `for (T x : iterable)` | `for x in iterable` (works with any iterator) |

## Key Rules / Gotchas Recap
- A `for` loop calls `iter()` then `next()` until `StopIteration`.
- Generators are lazy and one-shot; exhausted ones yield nothing, silently.
- `yield` inside a function makes it a generator function; calling it runs no code yet.
- Use generator expressions to avoid building large lists.
- `with` guarantees cleanup; prefer it for files, locks, connections.
- In `@contextmanager`, use `try/finally` around `yield`.
- `__exit__` returning `True` swallows the exception; do it deliberately.

## Why This Structure Exists
Streaming a large dataset, reading a model's token stream, paginating an API or scanning a big log file all use generators to avoid loading everything into memory. Context managers are how files, sockets, database transactions and locks are released safely in automation and security tools.
