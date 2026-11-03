# Tags: #Python #OOP #Modules #ClassesObjects | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Classes and objects: __init__, self, instance vs class attributes, methods,
and the shared-class-attribute trap."""


# ===== SECTION 1: A FIRST CLASS =====
class Dog:
    species = "Canis familiaris"  # class attribute: shared by all Dogs

    def __init__(self, name: str, age: int) -> None:
        self.name = name  # instance attributes: created by assignment
        self.age = age

    def bark(self) -> str:
        return f"{self.name} says woof"

    def birthday(self) -> None:
        self.age += 1


print("===== SECTION 1: A FIRST CLASS =====")
rex = Dog("Rex", 3)  # no 'new' keyword: just call the class
fido = Dog("Fido", 5)
print(rex.bark())
rex.birthday()
print("Rex age after birthday:", rex.age)
print("Fido age (separate object):", fido.age)
print("type(rex):", type(rex).__name__)


# ===== SECTION 2: SELF IS EXPLICIT =====
print("\n===== SECTION 2: SELF IS EXPLICIT =====")
print("rex.bark() ->", rex.bark())
print("Dog.bark(rex) ->", Dog.bark(rex))  # exactly what the first line does
print("Same result:", rex.bark() == Dog.bark(rex))


# ===== SECTION 3: INSTANCE VS CLASS ATTRIBUTES =====
print("\n===== SECTION 3: INSTANCE VS CLASS ATTRIBUTES =====")
print("rex.species:", rex.species)
print("Dog.species:", Dog.species)
rex.species = "Rex's own"  # creates an INSTANCE attribute that shadows the class one
print("After rex.species = ...: rex ->", rex.species, "| fido ->", fido.species)
print("rex.__dict__:", rex.__dict__)
del rex.species  # remove the shadow; lookup falls back to the class
print("After del: rex ->", rex.species)
Dog.species = "Changed on class"
print("Change on class is seen by fido:", fido.species)


# ===== SECTION 4: TRAP - MUTABLE CLASS ATTRIBUTE SHARED BY ALL =====
print("\n===== SECTION 4: TRAP - MUTABLE CLASS ATTRIBUTE =====")


class BadBag:
    items = []  # ONE list shared by every instance

    def add(self, x: str) -> None:
        self.items.append(x)  # mutates the shared list, no assignment


a, b = BadBag(), BadBag()
a.add("apple")
print("b.items (b never added anything!):", b.items)
print("Same list object:", a.items is b.items)


class GoodBag:
    def __init__(self) -> None:
        self.items: list[str] = []  # one list PER instance

    def add(self, x: str) -> None:
        self.items.append(x)


c, d = GoodBag(), GoodBag()
c.add("apple")
print("d.items after fix:", d.items)


# ===== SECTION 5: COUNTING INSTANCES WITH A CLASS ATTRIBUTE =====
print("\n===== SECTION 5: A LEGITIMATE CLASS ATTRIBUTE =====")


class Counter:
    created = 0

    def __init__(self) -> None:
        Counter.created += 1  # write through the class, not self


Counter(), Counter(), Counter()
print("Counter.created:", Counter.created)

# Trap: self.created += 1 would READ the class value but WRITE an instance one.
class Oops:
    n = 0

    def __init__(self) -> None:
        self.n += 1


Oops(), Oops()
print("Oops.n after two instances (still 0!):", Oops.n)


# ===== SECTION 6: DYNAMIC ATTRIBUTES =====
print("\n===== SECTION 6: ATTRIBUTES CAN BE ADDED ANYWHERE =====")
rex.nickname = "Rexy"  # legal: no declared fields in Python
print("rex.nickname:", rex.nickname)
print("hasattr(fido, 'nickname'):", hasattr(fido, "nickname"))
try:
    print(fido.nickname)
except AttributeError as e:
    print("AttributeError:", e)
