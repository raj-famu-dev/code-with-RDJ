# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Inheritance: super(), overriding, multiple inheritance, and the MRO
(method resolution order, C3 linearization)."""
import json


# ===== SECTION 1: BASIC INHERITANCE AND OVERRIDING =====
print("===== SECTION 1: BASIC INHERITANCE AND OVERRIDING =====")


class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return f"{self.name} makes a sound"

    def describe(self) -> str:
        return f"[{type(self).__name__}] {self.speak()}"


class Dog(Animal):
    def speak(self) -> str:  # override: no @Override annotation needed
        return f"{self.name} barks"


class Puppy(Dog):
    def __init__(self, name: str, toy: str) -> None:
        super().__init__(name)  # explicit; Python never calls parent init for you
        self.toy = toy

    def speak(self) -> str:
        return super().speak() + " squeakily"


print(Animal("Generic").describe())
print(Dog("Rex").describe())
print(Puppy("Bit", "ball").describe())
print("isinstance(Puppy, Animal):", isinstance(Puppy("a", "b"), Animal))
print("issubclass(Puppy, Dog):", issubclass(Puppy, Dog))


# ===== SECTION 2: TRAP - FORGETTING super().__init__ =====
print("\n===== SECTION 2: TRAP - FORGETTING super().__init__ =====")


class ForgetfulDog(Animal):
    def __init__(self, toy: str) -> None:
        self.toy = toy  # never called Animal.__init__


fd = ForgetfulDog("stick")
try:
    print(fd.speak())
except AttributeError as e:
    print("AttributeError:", e)


# ===== SECTION 3: MULTIPLE INHERITANCE AND THE MRO =====
print("\n===== SECTION 3: MULTIPLE INHERITANCE AND THE MRO =====")


class A:
    def who(self) -> str:
        return "A"


class B(A):
    def who(self) -> str:
        return "B>" + super().who()


class C(A):
    def who(self) -> str:
        return "C>" + super().who()


class D(B, C):
    def who(self) -> str:
        return "D>" + super().who()


print("D().who():", D().who())
print("D.__mro__:", [k.__name__ for k in D.__mro__])
print("A appears once, last: the diamond is solved by C3 linearization.")


# ===== SECTION 4: super() MEANS "NEXT IN MRO", NOT "PARENT" =====
print("\n===== SECTION 4: super() IS NEXT-IN-MRO =====")
print("B().who():", B().who(), "(B alone: next is A)")
print("In D, B's super() goes to C, not A. Order of bases matters.")


class E(C, B):
    pass


print("E.__mro__:", [k.__name__ for k in E.__mro__])
print("E().who():", E().who())


# ===== SECTION 5: MIXINS =====
print("\n===== SECTION 5: MIXINS =====")


class JsonMixin:
    def to_json(self) -> str:
        return json.dumps(vars(self))


class User(JsonMixin):
    def __init__(self, name: str, level: int) -> None:
        self.name = name
        self.level = level


print(User("raj", 3).to_json())


# ===== SECTION 6: INCONSISTENT ORDER IS REJECTED =====
print("\n===== SECTION 6: MRO CONFLICT ERROR =====")
try:
    class Bad(A, D):  # A before its own subclass D: impossible to linearize
        pass
except TypeError as e:
    print("TypeError:", str(e).splitlines()[0])
