# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Decorators: function decorators, functools.wraps, decorators with arguments,
timing/retry/cache examples, class decorators, @staticmethod/@classmethod."""
import functools
import time
from typing import Any, Callable


# ===== SECTION 1: A DECORATOR IS JUST A FUNCTION THAT RETURNS A FUNCTION =====
print("===== SECTION 1: THE BASIC IDEA =====")


def shout(func: Callable[..., str]) -> Callable[..., str]:
    def wrapper(*args: Any, **kwargs: Any) -> str:
        return func(*args, **kwargs).upper() + "!"
    return wrapper


@shout
def greet(name: str) -> str:
    return f"hello {name}"


def greet2(name: str) -> str:
    return f"hello {name}"


greet2 = shout(greet2)  # exactly what @shout does
print(greet("raj"), "|", greet2("raj"))


# ===== SECTION 2: TRAP - LOSING METADATA, FIXED WITH functools.wraps =====
print("\n===== SECTION 2: functools.wraps =====")
print("Without wraps -> greet.__name__:", greet.__name__)


def shout_ok(func: Callable[..., str]) -> Callable[..., str]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        return func(*args, **kwargs).upper() + "!"
    return wrapper


@shout_ok
def greet3(name: str) -> str:
    """Say hello."""
    return f"hello {name}"


print("With wraps    -> greet3.__name__:", greet3.__name__, "| doc:", greet3.__doc__)
print("Original still reachable via __wrapped__:", greet3.__wrapped__("x"))


# ===== SECTION 3: TIMING DECORATOR =====
print("\n===== SECTION 3: TIMING =====")


def timed(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            print(f"  [measurement] {func.__name__} took {elapsed:.4f}s (varies per run)")
    return wrapper


@timed
def work(n: int) -> int:
    return sum(range(n))


print("result:", work(100_000))


# ===== SECTION 4: DECORATOR WITH ARGUMENTS (THREE LEVELS) =====
print("\n===== SECTION 4: DECORATOR WITH ARGUMENTS: RETRY =====")


def retry(times: int, exceptions: tuple[type[Exception], ...] = (Exception,)):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"  attempt {attempt} failed: {e}")
                    if attempt == times:
                        raise
        return wrapper
    return decorator


calls = {"n": 0}


@retry(times=3, exceptions=(ConnectionError,))
def flaky() -> str:
    calls["n"] += 1
    if calls["n"] < 3:
        raise ConnectionError(f"simulated failure #{calls['n']}")
    return "success"


print("flaky() ->", flaky())


@retry(times=2)
def always_fails() -> None:
    raise ValueError("nope")


try:
    always_fails()
except ValueError as e:
    print("gave up and re-raised:", e)


# ===== SECTION 5: CACHING =====
print("\n===== SECTION 5: CACHING WITH functools.cache =====")
executed = []


def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
    store: dict[Any, Any] = {}

    @functools.wraps(func)
    def wrapper(*args: Any) -> Any:
        if args not in store:
            store[args] = func(*args)
        return store[args]
    return wrapper


@memoize
def slow_square(n: int) -> int:
    executed.append(n)
    return n * n


print(slow_square(4), slow_square(4), slow_square(5))
print("function body actually ran for:", executed)


@functools.cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print("fib(80) with stdlib cache:", fib(80))
print("cache_info:", fib.cache_info())


# ===== SECTION 6: STACKING ORDER =====
print("\n===== SECTION 6: STACKING DECORATORS =====")


def tag(name: str):
    def deco(f: Callable[[], str]) -> Callable[[], str]:
        return lambda: f"<{name}>{f()}</{name}>"
    return deco


@tag("b")
@tag("i")
def text() -> str:
    return "hi"


print(text(), "(bottom decorator applies first)")


# ===== SECTION 7: CLASS DECORATORS =====
print("\n===== SECTION 7: CLASS DECORATORS =====")
registry: dict[str, type] = {}


def register(cls: type) -> type:
    registry[cls.__name__] = cls
    return cls


@register
class PluginA:
    pass


@register
class PluginB:
    pass


print("registry:", sorted(registry))


def add_repr(cls: type) -> type:
    def __repr__(self: Any) -> str:
        return f"{cls.__name__}({vars(self)})"
    cls.__repr__ = __repr__  # type: ignore[assignment]
    return cls


@add_repr
class Item:
    def __init__(self) -> None:
        self.a = 1


print(Item())


# ===== SECTION 8: @staticmethod AND @classmethod =====
print("\n===== SECTION 8: @staticmethod AND @classmethod =====")


class Date:
    def __init__(self, y: int, m: int, d: int) -> None:
        self.y, self.m, self.d = y, m, d

    @classmethod
    def from_string(cls, s: str) -> "Date":  # alternative constructor
        y, m, d = map(int, s.split("-"))
        return cls(y, m, d)

    @staticmethod
    def is_leap(year: int) -> bool:  # no self, no cls: just a namespaced function
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.y}-{self.m:02d}-{self.d:02d})"


class SpecialDate(Date):
    pass


print(Date.from_string("2026-11-02"))
print("classmethod respects subclass:", SpecialDate.from_string("2000-01-01"))
print("is_leap(2000), is_leap(1900), is_leap(2024):",
      Date.is_leap(2000), Date.is_leap(1900), Date.is_leap(2024))
