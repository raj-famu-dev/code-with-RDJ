# Tags: #Python #OOP #Modules #Dataclasses | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Dataclasses: @dataclass, frozen, field(default_factory), the mutable-default
trap, and comparison to Java records."""
from dataclasses import dataclass, field, replace, asdict, FrozenInstanceError


# ===== SECTION 1: WHAT @dataclass GENERATES =====
print("===== SECTION 1: WHAT @dataclass GENERATES =====")


@dataclass
class Point:
    x: int
    y: int = 0  # default value


p = Point(1, 2)
print("repr:", p)
print("equality by value:", Point(1, 2) == Point(1, 2))
print("default y:", Point(5))
p.x = 99  # mutable by default
print("mutated:", p)
print("asdict:", asdict(p))
print("replace:", replace(p, y=-1))


# ===== SECTION 2: FROZEN =====
print("\n===== SECTION 2: FROZEN (IMMUTABLE) =====")


@dataclass(frozen=True)
class Coord:
    lat: float
    lon: float


c = Coord(1.0, 2.0)
try:
    c.lat = 5.0  # type: ignore[misc]
except FrozenInstanceError as e:
    print("FrozenInstanceError:", e)
print("frozen is hashable, usable in a set:", len({c, Coord(1.0, 2.0)}))
print("plain @dataclass hash:", Point.__hash__)


# ===== SECTION 3: TRAP - MUTABLE DEFAULT =====
print("\n===== SECTION 3: TRAP - MUTABLE DEFAULT =====")
try:
    @dataclass
    class Bad:
        tags: list[str] = []  # shared one list for all instances

except ValueError as e:
    print("ValueError:", e)
print("Dataclasses refuse this on purpose. The same bug in a plain function:")


def add_tag(tag: str, tags: list[str] = []) -> list[str]:  # classic bug
    tags.append(tag)
    return tags


print("add_tag('a'):", add_tag("a"))
print("add_tag('b'):", add_tag("b"), "(the default list leaked between calls!)")


# ===== SECTION 4: FIX WITH default_factory =====
print("\n===== SECTION 4: field(default_factory=...) =====")


@dataclass
class Student:
    name: str
    grades: list[int] = field(default_factory=list)  # new list per instance
    id_: int = field(default=0, repr=False, compare=False)


s1, s2 = Student("A"), Student("B")
s1.grades.append(90)
print("s1:", s1)
print("s2 untouched:", s2)


# ===== SECTION 5: __post_init__, ORDERING, FIELD OPTIONS =====
print("\n===== SECTION 5: __post_init__ AND order=True =====")


@dataclass(order=True)
class Task:
    priority: int
    name: str = field(compare=False)
    done: bool = False

    def __post_init__(self) -> None:
        if self.priority < 0:
            raise ValueError("priority must be >= 0")


tasks = [Task(3, "c"), Task(1, "a"), Task(2, "b")]
print("sorted:", [t.name for t in sorted(tasks)])
try:
    Task(-1, "bad")
except ValueError as e:
    print("validated in __post_init__:", e)


# ===== SECTION 6: SLOTS AND KW_ONLY =====
print("\n===== SECTION 6: slots=True, kw_only=True =====")


@dataclass(slots=True, kw_only=True)
class Config:
    host: str
    port: int = 8080


cfg = Config(host="localhost")
print(cfg)
try:
    cfg.extra = 1  # type: ignore[attr-defined]
except AttributeError:
    print("slots=True blocks adding unknown attributes")
try:
    Config("localhost")  # type: ignore[misc]
except TypeError as e:
    print("kw_only:", e)


# ===== SECTION 7: A GOTCHA - TYPE HINTS ARE NOT ENFORCED =====
print("\n===== SECTION 7: TRAP - NO RUNTIME TYPE CHECKING =====")
bad = Point("not an int", None)  # type: ignore[arg-type]
print("Accepted without complaint:", bad)
print("Use a type checker (mypy/pyright) or validate in __post_init__.")
