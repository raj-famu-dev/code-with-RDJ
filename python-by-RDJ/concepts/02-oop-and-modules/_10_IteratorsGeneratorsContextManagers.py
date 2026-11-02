# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Iterators, generators, generator expressions, and context managers
(__enter__/__exit__ and contextlib.contextmanager)."""
import sys
from contextlib import contextmanager, suppress


# ===== SECTION 1: THE ITERATOR PROTOCOL =====
print("===== SECTION 1: THE ITERATOR PROTOCOL =====")
it = iter([10, 20])
print("next:", next(it), next(it))
try:
    next(it)
except StopIteration:
    print("StopIteration signals the end")
print("A for loop = iter() once, then next() until StopIteration.")


class Countdown:
    """Iterable AND iterator (one pass only)."""

    def __init__(self, start: int) -> None:
        self.cur = start

    def __iter__(self) -> "Countdown":
        return self

    def __next__(self) -> int:
        if self.cur <= 0:
            raise StopIteration
        self.cur -= 1
        return self.cur + 1


cd = Countdown(3)
print("first pass:", list(cd))
print("second pass (exhausted!):", list(cd))


# ===== SECTION 2: GENERATORS =====
print("\n===== SECTION 2: GENERATORS =====")


def countdown(n: int):
    print("  (generator body starts only on first next)")
    while n > 0:
        yield n  # pauses here, keeps local state
        n -= 1


g = countdown(3)
print("created generator, nothing ran yet:", type(g).__name__)
print("next:", next(g))
print("rest:", list(g))
print("exhausted:", list(g))


def fib():
    a, b = 0, 1
    while True:  # infinite is fine: values produced lazily
        yield a
        a, b = b, a + b


gen = fib()
print("first 10 Fibonacci:", [next(gen) for _ in range(10)])


def passthrough():
    yield 1
    yield from [2, 3]  # delegate to another iterable
    return "done"


print("yield from:", list(passthrough()))


# ===== SECTION 3: GENERATOR EXPRESSIONS =====
print("\n===== SECTION 3: GENERATOR EXPRESSIONS =====")
squares_list = [n * n for n in range(1000)]
squares_gen = (n * n for n in range(1000))
print("sum via list:", sum(squares_list), "| via generator:", sum(squares_gen))
print("sys.getsizeof list > generator:",
      sys.getsizeof(squares_list) > sys.getsizeof(squares_gen),
      "(sizes are a measurement of this interpreter; exact bytes not claimed)")
print("any() short-circuits:", any(n > 5 for n in range(10**9)))


# ===== SECTION 4: TRAP - GENERATORS ARE ONE-SHOT =====
print("\n===== SECTION 4: TRAP - ONE-SHOT =====")
evens = (n for n in range(10) if n % 2 == 0)
print("first use:", list(evens))
print("second use:", list(evens), "<- silently empty!")
print("Fix: store a list, or call the generator function again.")


# ===== SECTION 5: CONTEXT MANAGER WITH __enter__/__exit__ =====
print("\n===== SECTION 5: CLASS-BASED CONTEXT MANAGER =====")


class Resource:
    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> "Resource":
        print(f"  open {self.name}")
        return self  # bound to the 'as' variable

    def __exit__(self, exc_type, exc, tb) -> bool:
        print(f"  close {self.name} (exception: {exc_type.__name__ if exc_type else None})")
        return exc_type is ValueError  # True swallows the exception


with Resource("db") as r:
    print("  using", r.name)

with Resource("db2"):
    raise ValueError("swallowed by __exit__")
print("execution continued after the with block")

try:
    with Resource("db3"):
        raise KeyError("not swallowed")
except KeyError:
    print("KeyError propagated, but cleanup still ran")


# ===== SECTION 6: contextlib.contextmanager =====
print("\n===== SECTION 6: @contextmanager =====")


@contextmanager
def managed(name: str):
    print(f"  setup {name}")
    try:
        yield name.upper()
    finally:  # without try/finally, cleanup is skipped on exceptions
        print(f"  teardown {name}")


with managed("conn") as value:
    print("  got", value)
try:
    with managed("conn2"):
        raise RuntimeError("boom")
except RuntimeError:
    print("teardown ran despite the error")

with suppress(ZeroDivisionError):
    1 / 0
print("contextlib.suppress ignored ZeroDivisionError")


# ===== SECTION 7: TRAP - FORGETTING with FOR FILES =====
print("\n===== SECTION 7: with AND FILES =====")
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "x.txt"
    with open(p, "w", encoding="utf-8") as f:
        f.write("hello")
    print("closed after with:", f.closed)
    leaked = open(p, encoding="utf-8")
    print("manual open without with, closed?", leaked.closed)
    leaked.close()  # must remember; with does it automatically
