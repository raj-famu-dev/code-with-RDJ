# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Abstract base classes with abc.ABC and @abstractmethod, and why trying to
instantiate an incomplete subclass fails."""
from abc import ABC, abstractmethod


# ===== SECTION 1: AN ABSTRACT BASE CLASS =====
print("===== SECTION 1: AN ABSTRACT BASE CLASS =====")


class Shape(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def area(self) -> float:
        """Subclasses must implement."""

    def describe(self) -> str:  # concrete method shared by subclasses
        return f"{self.name} with area {self.area():.2f}"


class Circle(Shape):
    def __init__(self, r: float) -> None:
        super().__init__("Circle")
        self.r = r

    def area(self) -> float:
        return 3.14159 * self.r ** 2


print(Circle(2).describe())


# ===== SECTION 2: WHY INSTANTIATION FAILS =====
print("\n===== SECTION 2: INSTANTIATION FAILS =====")
try:
    Shape("x")
except TypeError as e:
    print("TypeError:", e)
print("Shape.__abstractmethods__:", set(Shape.__abstractmethods__))


# ===== SECTION 3: TRAP - INCOMPLETE SUBCLASS =====
print("\n===== SECTION 3: TRAP - INCOMPLETE SUBCLASS =====")


class Lazy(Shape):
    pass  # forgot area()


try:
    Lazy("lazy")
except TypeError as e:
    print("TypeError:", e)


class Fixed(Lazy):
    def area(self) -> float:
        return 1.0


print("After implementing area():", Fixed("fixed").describe())


# ===== SECTION 4: WITHOUT ABC, @abstractmethod IS NOT ENFORCED =====
print("\n===== SECTION 4: TRAP - FORGETTING ABC =====")


class NotReallyAbstract:  # missing ABC base: decorator does nothing
    @abstractmethod
    def f(self) -> int: ...


print("Instantiated fine:", type(NotReallyAbstract()).__name__)
print("Enforcement comes from the ABCMeta metaclass, not the decorator alone.")


# ===== SECTION 5: ABSTRACT METHOD WITH A BODY =====
print("\n===== SECTION 5: ABSTRACT METHODS CAN HAVE CODE =====")


class Logger(ABC):
    @abstractmethod
    def write(self, msg: str) -> None:
        print("[base] shared prefix work, then:", msg)


class ConsoleLogger(Logger):
    def write(self, msg: str) -> None:
        super().write(msg)  # reuse the base body deliberately
        print("[console]", msg)


ConsoleLogger().write("hello")


# ===== SECTION 6: ABSTRACT PROPERTY, ISINSTANCE, AND register =====
print("\n===== SECTION 6: ABSTRACT PROPERTY AND register =====")


class Named(ABC):
    @property
    @abstractmethod
    def label(self) -> str: ...


class Tag(Named):
    @property
    def label(self) -> str:
        return "tag-1"


print("Tag().label:", Tag().label)
print("isinstance(Tag(), Named):", isinstance(Tag(), Named))


class Foreign:
    label = "foreign"


Named.register(Foreign)  # declare it a virtual subclass, no inheritance
print("isinstance(Foreign(), Named) after register:", isinstance(Foreign(), Named))
