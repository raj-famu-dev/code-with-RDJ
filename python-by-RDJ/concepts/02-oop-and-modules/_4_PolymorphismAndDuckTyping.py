# Tags: #Python #OOP #Modules #PolymorphismDuckTyping | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Polymorphism in Python: duck typing, typing.Protocol (structural typing),
and how both differ from Java interfaces."""
from typing import Protocol, runtime_checkable


# ===== SECTION 1: DUCK TYPING =====
print("===== SECTION 1: DUCK TYPING =====")


class Duck:
    def speak(self) -> str:
        return "Quack"


class Robot:  # unrelated to Duck: no shared base class
    def speak(self) -> str:
        return "Beep"


def make_noise(thing) -> str:  # no declared type needed
    return thing.speak()


for obj in (Duck(), Robot()):
    print(type(obj).__name__, "->", make_noise(obj))


# ===== SECTION 2: TRAP - DUCK TYPING FAILS AT RUNTIME =====
print("\n===== SECTION 2: TRAP - FAILS AT CALL TIME =====")
try:
    make_noise(42)
except AttributeError as e:
    print("AttributeError:", e)
print("No compiler to catch this: that is what Protocol + a type checker add.")


# ===== SECTION 3: PROTOCOL (STRUCTURAL TYPING) =====
print("\n===== SECTION 3: PROTOCOL =====")


@runtime_checkable
class Speaker(Protocol):
    def speak(self) -> str: ...


def announce(s: Speaker) -> str:
    return "Announcing: " + s.speak()


print(announce(Duck()))
print(announce(Robot()))
# Neither Duck nor Robot says "implements Speaker". Matching shape is enough;
# a checker such as mypy/pyright would verify this before running.


# ===== SECTION 4: runtime_checkable AND ITS LIMIT =====
print("\n===== SECTION 4: isinstance WITH A PROTOCOL =====")
print("isinstance(Duck(), Speaker):", isinstance(Duck(), Speaker))
print("isinstance(42, Speaker):", isinstance(42, Speaker))


class FakeSpeaker:
    speak = "I am a string, not a method"


print("isinstance(FakeSpeaker(), Speaker):", isinstance(FakeSpeaker(), Speaker),
      "(only checks the NAME exists, not the signature)")


# ===== SECTION 5: POLYMORPHISM VIA A COMMON LOOP =====
print("\n===== SECTION 5: POLYMORPHIC LOOP =====")


class Shape(Protocol):
    def area(self) -> float: ...


class Square:
    def __init__(self, s: float) -> None:
        self.s = s

    def area(self) -> float:
        return self.s ** 2


class Rect:
    def __init__(self, w: float, h: float) -> None:
        self.w, self.h = w, h

    def area(self) -> float:
        return self.w * self.h


def total_area(shapes: list[Shape]) -> float:
    return sum(sh.area() for sh in shapes)


print("total area:", total_area([Square(2), Rect(3, 4)]))


# ===== SECTION 6: BUILT-INS ARE DUCK TYPED =====
print("\n===== SECTION 6: BUILT-IN DUCK TYPING =====")


class Countdown:
    def __init__(self, n: int) -> None:
        self.n = n

    def __len__(self) -> int:
        return self.n


print("len(Countdown(5)):", len(Countdown(5)), "(len() just needs __len__)")
print("bool(Countdown(0)):", bool(Countdown(0)), "(falsy because __len__ is 0)")
