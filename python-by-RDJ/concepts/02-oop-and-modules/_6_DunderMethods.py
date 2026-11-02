# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Dunder (magic) methods: __str__/__repr__, __eq__ + __hash__, ordering with
functools.total_ordering, __len__, __iter__, __getitem__, __add__."""
from functools import total_ordering


# ===== SECTION 1: __str__ VS __repr__ =====
print("===== SECTION 1: __str__ VS __repr__ =====")


class Money:
    def __init__(self, cents: int) -> None:
        self.cents = cents

    def __repr__(self) -> str:  # for developers: unambiguous
        return f"Money({self.cents})"

    def __str__(self) -> str:  # for users: readable
        return f"${self.cents / 100:.2f}"


m = Money(1999)
print("print(m)  ->", m)
print("repr(m)   ->", repr(m))
print("in a list ->", [m, Money(5)], "(containers use repr)")
print("f-string  ->", f"{m} / {m!r}")


class OnlyDefault:
    pass


print("default repr has an address, so only its prefix is shown:",
      repr(OnlyDefault()).split(" at ")[0])


# ===== SECTION 2: __eq__ + __hash__ PAIRING TRAP =====
print("\n===== SECTION 2: __eq__ + __hash__ TRAP =====")


class P1:
    def __init__(self, x: int) -> None:
        self.x = x

    def __eq__(self, other: object) -> bool:
        return isinstance(other, P1) and self.x == other.x


print("P1(1) == P1(1):", P1(1) == P1(1))
try:
    {P1(1)}
except TypeError as e:
    print("Defining __eq__ alone sets __hash__ = None ->", e)
print("P1.__hash__ is None:", P1.__hash__ is None)


class P2:
    def __init__(self, x: int) -> None:
        self.x = x

    def __eq__(self, other: object) -> bool:
        return isinstance(other, P2) and self.x == other.x

    def __hash__(self) -> int:
        return hash(self.x)  # must be consistent with __eq__


print("Set of P2(1), P2(1), P2(2) has size:", len({P2(1), P2(1), P2(2)}))
d = {P2(7): "seven"}
print("dict lookup with an equal but different object:", d[P2(7)])
print("Hash only works if the fields are not mutated while in a set/dict.")


# ===== SECTION 3: ORDERING WITH total_ordering =====
print("\n===== SECTION 3: ORDERING =====")


@total_ordering
class Version:
    def __init__(self, major: int, minor: int) -> None:
        self.t = (major, minor)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Version) and self.t == other.t

    def __lt__(self, other: "Version") -> bool:
        return self.t < other.t

    def __hash__(self) -> int:
        return hash(self.t)

    def __repr__(self) -> str:
        return f"v{self.t[0]}.{self.t[1]}"


vs = [Version(2, 1), Version(1, 9), Version(2, 0)]
print("sorted:", sorted(vs))
print("max:", max(vs))
print("v1.9 <= v2.0 (derived by total_ordering):", Version(1, 9) <= Version(2, 0))
print("v2.0 > v1.9 (derived):", Version(2, 0) > Version(1, 9))


# ===== SECTION 4: __len__, __getitem__, __iter__ =====
print("\n===== SECTION 4: CONTAINER PROTOCOL =====")


class Playlist:
    def __init__(self, *songs: str) -> None:
        self._songs = list(songs)

    def __len__(self) -> int:
        return len(self._songs)

    def __getitem__(self, i):  # int or slice
        return self._songs[i]

    def __iter__(self):
        return iter(self._songs)

    def __contains__(self, s: object) -> bool:
        return s in self._songs


pl = Playlist("a", "b", "c", "d")
print("len:", len(pl))
print("pl[0]:", pl[0], "| pl[-1]:", pl[-1], "| pl[1:3]:", pl[1:3])
print("for loop:", [s.upper() for s in pl])
print("'c' in pl:", "c" in pl)
print("list(pl):", list(pl))


class OnlyGetItem:  # old-style iteration fallback
    def __getitem__(self, i: int) -> int:
        if i >= 3:
            raise IndexError
        return i * 10


print("Iterates with only __getitem__:", list(OnlyGetItem()))


# ===== SECTION 5: OPERATOR OVERLOADING =====
print("\n===== SECTION 5: __add__ AND FRIENDS =====")


class Vec:
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y

    def __add__(self, other: "Vec") -> "Vec":
        if not isinstance(other, Vec):
            return NotImplemented  # lets Python try the other side / raise TypeError
        return Vec(self.x + other.x, self.y + other.y)

    def __mul__(self, k: float) -> "Vec":
        return Vec(self.x * k, self.y * k)

    def __rmul__(self, k: float) -> "Vec":  # supports 3 * v
        return self * k

    def __bool__(self) -> bool:
        return bool(self.x or self.y)

    def __repr__(self) -> str:
        return f"Vec({self.x}, {self.y})"


print("Vec(1,2) + Vec(3,4) =", Vec(1, 2) + Vec(3, 4))
print("Vec(1,2) * 3 =", Vec(1, 2) * 3)
print("3 * Vec(1,2) =", 3 * Vec(1, 2), "(needs __rmul__)")
print("bool(Vec(0,0)):", bool(Vec(0, 0)))
try:
    Vec(1, 1) + 5
except TypeError as e:
    print("TypeError:", e)
