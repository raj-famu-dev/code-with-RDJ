# `_7_Dataclasses.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A dataclass is a class whose boilerplate is written for you. Putting `@dataclass` above a class with annotated fields generates `__init__`, `__repr__` and `__eq__` automatically, with options for ordering, immutability (`frozen=True`), memory savings (`slots=True`) and keyword-only fields.

They are Python's everyday way to model plain data, and the closest relative of Java records, though they are more flexible and less strict.

## Full Line-by-Line Breakdown

### SECTION 1: WHAT @dataclass GENERATES
From `x: int` and `y: int = 0` Python builds the constructor, a readable `repr`, and value-based `==`. Defaults are supported. By default instances are mutable. `asdict` converts to a dictionary (useful for JSON), and `replace` creates a modified copy without changing the original.

Output from a real run:

```text
===== SECTION 1: WHAT @dataclass GENERATES =====
repr: Point(x=1, y=2)
equality by value: True
default y: Point(x=5, y=0)
mutated: Point(x=99, y=2)
asdict: {'x': 99, 'y': 2}
replace: Point(x=99, y=-1)
```

### SECTION 2: FROZEN (IMMUTABLE)
`frozen=True` makes assignment raise `FrozenInstanceError` and also makes the class hashable, so instances work in sets and as dict keys. A normal mutable dataclass sets `__hash__` to `None` (the same rule as `__eq__` without `__hash__`).

Output from a real run:

```text
===== SECTION 2: FROZEN (IMMUTABLE) =====
FrozenInstanceError: cannot assign to field 'lat'
frozen is hashable, usable in a set: 1
plain @dataclass hash: None
```

### SECTION 3: TRAP - MUTABLE DEFAULT
A default like `tags: list = []` would be shared by all instances, so dataclasses refuse it with `ValueError`. The second half shows the identical bug in a normal function: a default argument is created ONCE when the function is defined, so the list leaks between calls (`['a', 'b']`). This is one of the most famous Python traps. Fix with `None` plus creating the list inside, or in dataclasses with `default_factory`.

Output from a real run:

```text
===== SECTION 3: TRAP - MUTABLE DEFAULT =====
ValueError: mutable default <class 'list'> for field tags is not allowed: use default_factory
Dataclasses refuse this on purpose. The same bug in a plain function:
add_tag('a'): ['a']
add_tag('b'): ['a', 'b'] (the default list leaked between calls!)
```

### SECTION 4: field(default_factory=...)
`field(default_factory=list)` calls `list()` for each new object, so every `Student` gets its own list. `field` also controls `repr`, `compare`, `init` and more. `id_` here is excluded from the repr and from equality.

Output from a real run:

```text
===== SECTION 4: field(default_factory=...) =====
s1: Student(name='A', grades=[90])
s2 untouched: Student(name='B', grades=[])
```

### SECTION 5: __post_init__ AND order=True
`__post_init__` runs right after the generated `__init__`; it is the place for validation or derived fields. `order=True` generates `<`, `<=`, `>`, `>=` comparing fields in declaration order, here only `priority` because `name` has `compare=False`.

Output from a real run:

```text
===== SECTION 5: __post_init__ AND order=True =====
sorted: ['a', 'b', 'c']
validated in __post_init__: priority must be >= 0
```

### SECTION 6: slots=True, kw_only=True
`slots=True` removes the per-object dictionary, saving memory and blocking accidental new attributes. `kw_only=True` forces callers to name each argument, which prevents argument-order mistakes. Both options are available in Python 3.10 and later.

Output from a real run:

```text
===== SECTION 6: slots=True, kw_only=True =====
Config(host='localhost', port=8080)
slots=True blocks adding unknown attributes
kw_only: Config.__init__() takes 1 positional argument but 2 were given
```

### SECTION 7: TRAP - NO RUNTIME TYPE CHECKING
The annotations are hints for tools, not rules for the interpreter. `Point("not an int", None)` is accepted. If you need real runtime validation check in `__post_init__` or use a library such as Pydantic.

Output from a real run:

```text
===== SECTION 7: TRAP - NO RUNTIME TYPE CHECKING =====
Accepted without complaint: Point(x='not an int', y=None)
Use a type checker (mypy/pyright) or validate in __post_init__.
```

## Key Differences From Java
| Java | Python |
|---|---|
| `record Point(int x, int y) {}` (always immutable) | `@dataclass` (mutable by default) or `@dataclass(frozen=True)` |
| Record auto-generates constructor, accessors, `equals`, `hashCode`, `toString` | Generates `__init__`, `__repr__`, `__eq__` (and `__hash__` only if frozen) |
| Field types enforced by compiler | Type hints are NOT enforced at runtime |
| Compact constructor for validation | `__post_init__` |
| Lombok `@Data`, `@Builder` | `@dataclass`, `replace`, keyword-only fields |
| Records cannot extend classes | Dataclasses can inherit and be extended |
| Default `new ArrayList<>()` in constructor | `field(default_factory=list)` |

## Key Rules / Gotchas Recap
- Use `default_factory` for list, dict and set defaults.
- `frozen=True` gives immutability and hashing.
- Fields without defaults must come before fields with defaults (unless `kw_only`).
- Annotations are not checked when running.
- `@dataclass` generates `__eq__`, so a mutable dataclass is unhashable by default.
- Function default arguments are evaluated once: never use `[]` or `{}` as a default.

## Why This Structure Exists
Configuration objects, API responses, evaluation records and agent messages are plain data, so dataclasses remove the boilerplate and make code readable and testable.
