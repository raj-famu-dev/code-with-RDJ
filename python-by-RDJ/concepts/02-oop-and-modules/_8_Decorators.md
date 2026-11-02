# `_8_Decorators.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A decorator is a function that takes a function (or class) and returns a replacement, usually one that wraps the original with extra behaviour. The `@name` line above a definition is shorthand for `f = name(f)`. Because functions are ordinary objects in Python, decorators are used everywhere for timing, logging, caching, retries, access control and registration.

Two built-in decorators, `@staticmethod` and `@classmethod`, change how methods receive their first argument.

## Full Line-by-Line Breakdown

### SECTION 1: THE BASIC IDEA
`shout` takes `func` and returns `wrapper`, which calls `func` and changes the result. The `@shout` line and the manual `greet2 = shout(greet2)` do exactly the same thing, as the identical output shows. `*args, **kwargs` lets the wrapper forward any arguments.

Output from a real run:

```text
===== SECTION 1: THE BASIC IDEA =====
HELLO RAJ! | HELLO RAJ!
```

### SECTION 2: functools.wraps
A naive wrapper replaces the function, so its name becomes `wrapper` and the docstring disappears. That breaks debugging, documentation and tools. `@functools.wraps(func)` copies the name, docstring and other metadata and stores the original in `__wrapped__`. Always use it.

Output from a real run:

```text
===== SECTION 2: functools.wraps =====
Without wraps -> greet.__name__: wrapper
With wraps    -> greet3.__name__: greet3 | doc: Say hello.
Original still reachable via __wrapped__: hello x
```

### SECTION 3: TIMING
`timed` measures with `time.perf_counter()` and prints the elapsed time in a `finally` block so it prints even if the function raises. The seconds value is a measurement and changes every run; the result `4999950000` is deterministic.

Output from a real run:

```text
===== SECTION 3: TIMING =====
  [measurement] work took 0.0019s (varies per run)
result: 4999950000
```

### SECTION 4: DECORATOR WITH ARGUMENTS: RETRY
`@retry(times=3)` first CALLS `retry(...)`, which returns the real decorator, which returns the wrapper: three nested functions. The wrapper retries on the listed exceptions and re-raises on the last attempt. `flaky` fails twice (simulated, no network) then succeeds; `always_fails` exhausts its attempts and the original `ValueError` propagates.

Output from a real run:

```text
===== SECTION 4: DECORATOR WITH ARGUMENTS: RETRY =====
  attempt 1 failed: simulated failure #1
  attempt 2 failed: simulated failure #2
flaky() -> success
  attempt 1 failed: nope
  attempt 2 failed: nope
gave up and re-raised: nope
```

### SECTION 5: CACHING WITH functools.cache
`memoize` stores results keyed by arguments, so the body runs only for new inputs (`[4, 5]`, not `[4, 4, 5]`). The standard library already ships `functools.cache` (unbounded) and `functools.lru_cache(maxsize=...)`. With the cache, recursive `fib(80)` returns instantly; `cache_info()` shows hits and misses. Arguments must be hashable, and cached results of impure functions can be stale.

Output from a real run:

```text
===== SECTION 5: CACHING WITH functools.cache =====
16 16 25
function body actually ran for: [4, 5]
fib(80) with stdlib cache: 23416728348467685
cache_info: CacheInfo(hits=78, misses=81, maxsize=None, currsize=81)
```

### SECTION 6: STACKING DECORATORS
Decorators apply from the bottom up: `@tag("i")` wraps `text` first, then `@tag("b")` wraps that, so `b` ends up outermost.

Output from a real run:

```text
===== SECTION 6: STACKING DECORATORS =====
<b><i>hi</i></b> (bottom decorator applies first)
```

### SECTION 7: CLASS DECORATORS
A decorator can receive a class instead of a function. `register` records the class in a dictionary and returns it unchanged (a simple plugin registry). `add_repr` modifies the class by attaching a method. `@dataclass` is itself a class decorator.

Output from a real run:

```text
===== SECTION 7: CLASS DECORATORS =====
registry: ['PluginA', 'PluginB']
Item({'a': 1})
```

### SECTION 8: @staticmethod AND @classmethod
A `@classmethod` receives the class as `cls`, so it can build instances and works correctly for subclasses (`SpecialDate.from_string` returns a `SpecialDate`); this is the standard pattern for alternative constructors. A `@staticmethod` receives neither `self` nor `cls`; it is just a function placed in the class namespace for organisation.

Output from a real run:

```text
===== SECTION 8: @staticmethod AND @classmethod =====
Date(2026-11-02)
classmethod respects subclass: SpecialDate(2000-01-01)
is_leap(2000), is_leap(1900), is_leap(2024): True False True
```

## Key Differences From Java
| Java | Python |
|---|---|
| Annotations (`@Override`) are metadata, they do nothing by themselves | Decorators are executable functions that replace the thing they decorate |
| Cross-cutting behaviour via AOP/Spring proxies | A 5-line decorator |
| Overloaded constructors | `@classmethod` alternative constructors (`from_string`) |
| `static` method | `@staticmethod` (rarely needed; a module-level function is often better) |
| `static` methods are not polymorphic | `@classmethod` gets the real subclass via `cls` |
| Memoization needs a library or manual map | `functools.cache` in the standard library |

## Key Rules / Gotchas Recap
- `@d` above `f` means `f = d(f)`.
- Always add `@functools.wraps(func)` in your wrapper.
- A decorator with arguments has three levels: factory, decorator, wrapper.
- Stacked decorators apply bottom-up.
- Wrapper should return the result of the wrapped call.
- Cache keys must be hashable; do not cache functions with side effects.
- Use `finally` when a wrapper must clean up or log even on exceptions.

## Why This Structure Exists
Decorators are everywhere in modern Python tooling: web routes (`@app.get`), test fixtures (`@pytest.fixture`), retries around flaky LLM API calls, rate-limiting, caching expensive embedding calls and registering agent tools.
