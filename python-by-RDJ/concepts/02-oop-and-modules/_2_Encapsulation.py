# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Encapsulation in Python: naming conventions, name mangling, and @property
for validated attributes. Python has no private keyword."""


# ===== SECTION 1: UNDERSCORE CONVENTIONS =====
print("===== SECTION 1: UNDERSCORE CONVENTIONS =====")


class Account:
    def __init__(self, owner: str) -> None:
        self.owner = owner  # public
        self._balance = 0  # "protected" by convention only
        self.__pin = "1234"  # name-mangled

    def pin_matches(self, guess: str) -> bool:
        return self.__pin == guess


acct = Account("Raj")
print("public acct.owner:", acct.owner)
print("single underscore still reachable:", acct._balance)
try:
    print(acct.__pin)
except AttributeError as e:
    print("acct.__pin -> AttributeError:", e)


# ===== SECTION 2: NAME MANGLING IS NOT SECURITY =====
print("\n===== SECTION 2: NAME MANGLING IS NOT SECURITY =====")
print("vars:", sorted(vars(acct)))
print("acct._Account__pin:", acct._Account__pin)  # trivially reachable
print("pin_matches('1234'):", acct.pin_matches("1234"))


# ===== SECTION 3: WHY MANGLING EXISTS =====
print("\n===== SECTION 3: MANGLING AVOIDS SUBCLASS COLLISIONS =====")


class Base:
    def __init__(self) -> None:
        self.__secret = "base"

    def base_secret(self) -> str:
        return self.__secret


class Child(Base):
    def __init__(self) -> None:
        super().__init__()
        self.__secret = "child"  # becomes _Child__secret, no clobbering


ch = Child()
print("base_secret():", ch.base_secret())
print("vars:", sorted(vars(ch)))


# ===== SECTION 4: TRAP - GETTER/SETTER BOILERPLATE =====
print("\n===== SECTION 4: PLAIN ATTRIBUTES FIRST =====")


class Point:
    def __init__(self, x: float) -> None:
        self.x = x  # no getX()/setX() needed in Python


p = Point(1.5)
p.x = 2.5
print("p.x:", p.x)
print("You can add validation LATER with @property without changing callers.")


# ===== SECTION 5: @PROPERTY WITH VALIDATION =====
print("\n===== SECTION 5: @PROPERTY WITH VALIDATION =====")


class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius  # goes through the setter

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:  # read-only computed property
        return self._celsius * 9 / 5 + 32


t = Temperature(100)
print("celsius:", t.celsius, "| fahrenheit:", t.fahrenheit)
t.celsius = 0
print("after set 0 -> fahrenheit:", t.fahrenheit)
try:
    t.celsius = -300
except ValueError as e:
    print("setter rejected:", e)
try:
    Temperature(-500)
except ValueError as e:
    print("constructor also validated:", e)
try:
    t.fahrenheit = 50  # type: ignore[misc]
except AttributeError as e:
    print("read-only property:", e)


# ===== SECTION 6: TRAP - FORGETTING THE UNDERSCORE (INFINITE RECURSION) =====
print("\n===== SECTION 6: TRAP - PROPERTY RECURSION =====")


class Broken:
    @property
    def v(self) -> int:
        return self.v  # calls itself forever

try:
    Broken().v
except RecursionError:
    print("RecursionError: property returned itself instead of self._v")


# ===== SECTION 7: DELETER AND LAZY COMPUTE =====
print("\n===== SECTION 7: DELETER =====")


class Profile:
    def __init__(self) -> None:
        self._nick: str | None = "rdj"

    @property
    def nick(self) -> str | None:
        return self._nick

    @nick.deleter
    def nick(self) -> None:
        print("deleting nick")
        self._nick = None


pr = Profile()
del pr.nick
print("nick now:", pr.nick)
