# `_1_ClassesAndObjects.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A class is a blueprint and an object is one thing built from it. In Python you create objects by calling the class like a function (no `new`), `__init__` sets up each object, and `self` is the object a method is working on. Attributes are not declared up front: they come into existence when you assign them.

There are two kinds of attributes. Instance attributes (set through `self`) belong to one object. Class attributes (set in the class body) are shared by all objects, which is useful for constants and counters and dangerous for mutable values.

## Full Line-by-Line Breakdown

### SECTION 1: A FIRST CLASS
`Dog` has a class attribute `species` and an `__init__` that stores `name` and `age` on `self`. `Dog("Rex", 3)` creates the object and runs `__init__` for you. `bark` and `birthday` are ordinary methods whose first parameter is `self`. `rex` and `fido` each have their own `age`, so changing Rex does not touch Fido. `type(rex).__name__` shows the class that built the object.

Output from a real run:

```text
===== SECTION 1: A FIRST CLASS =====
Rex says woof
Rex age after birthday: 4
Fido age (separate object): 5
type(rex): Dog
```

### SECTION 2: SELF IS EXPLICIT
`rex.bark()` is shorthand for `Dog.bark(rex)`. Python passes the object as the first argument automatically; the name `self` is only a convention, but everybody uses it. Both lines print the same string, which proves it.

Output from a real run:

```text
===== SECTION 2: SELF IS EXPLICIT =====
rex.bark() -> Rex says woof
Dog.bark(rex) -> Rex says woof
Same result: True
```

### SECTION 3: INSTANCE VS CLASS ATTRIBUTES
Reading `rex.species` looks on the object first, then on the class. Assigning `rex.species = ...` does NOT change the class; it creates a new instance attribute that hides (shadows) the class one, as `rex.__dict__` shows. `del rex.species` removes the shadow and the lookup falls back to the class. Assigning on the class (`Dog.species = ...`) changes what every object without its own copy sees.

Output from a real run:

```text
===== SECTION 3: INSTANCE VS CLASS ATTRIBUTES =====
rex.species: Canis familiaris
Dog.species: Canis familiaris
After rex.species = ...: rex -> Rex's own | fido -> Canis familiaris
rex.__dict__: {'name': 'Rex', 'age': 4, 'species': "Rex's own"}
After del: rex -> Canis familiaris
Change on class is seen by fido: Changed on class
```

### SECTION 4: TRAP - MUTABLE CLASS ATTRIBUTE
`BadBag.items = []` creates ONE list on the class. `self.items.append(...)` mutates that shared list; no assignment happens, so no per-object copy is made. Adding to bag `a` therefore shows up in bag `b`, and `a.items is b.items` is `True`. The fix (`GoodBag`) creates the list inside `__init__` so every object gets its own.

Output from a real run:

```text
===== SECTION 4: TRAP - MUTABLE CLASS ATTRIBUTE =====
b.items (b never added anything!): ['apple']
Same list object: True
d.items after fix: []
```

### SECTION 5: A LEGITIMATE CLASS ATTRIBUTE
A counter shared by all objects is a good use of a class attribute. Writing `Counter.created += 1` updates the single shared value (3 after three objects). `Oops` shows the sibling trap: `self.n += 1` reads the class value 0, adds 1, and WRITES the result as a new instance attribute, so the class value never changes.

Output from a real run:

```text
===== SECTION 5: A LEGITIMATE CLASS ATTRIBUTE =====
Counter.created: 3
Oops.n after two instances (still 0!): 0
```

### SECTION 6: ATTRIBUTES CAN BE ADDED ANYWHERE
Python objects are open: `rex.nickname = ...` just works, and `fido` does not get it. Reading a missing attribute raises `AttributeError`. This flexibility is why typos in attribute names are silent bugs when you assign (`self.nmae = x` creates a new attribute).

Output from a real run:

```text
===== SECTION 6: ATTRIBUTES CAN BE ADDED ANYWHERE =====
rex.nickname: Rexy
hasattr(fido, 'nickname'): False
AttributeError: 'Dog' object has no attribute 'nickname'
```

## Key Differences From Java
| Java | Python |
|---|---|
| `new Dog("Rex", 3)` | `Dog("Rex", 3)` (no `new`) |
| Constructor named after the class, overloads allowed | One `__init__`; use default arguments or classmethods instead of overloads |
| `this` is implicit | `self` is an explicit first parameter and is not a keyword |
| Fields declared in the class body with types | Instance attributes are created by assignment, usually in `__init__` |
| `static` field | Class attribute (assigned in the class body) |
| Compiler rejects unknown fields | Any attribute can be added at runtime; typos are not caught |
| `private`/`public` modifiers | Only naming conventions (see `_2_Encapsulation`) |

## Key Rules / Gotchas Recap
- No `new`; call the class.
- `self` is always the first parameter of an instance method, and you must write it.
- Assign instance state in `__init__` through `self`.
- Never put a mutable value (list, dict, set) in the class body unless you really want it shared.
- `self.x = ...` creates or updates an INSTANCE attribute; to change a class attribute write `ClassName.x = ...`.
- Reading falls back from instance to class; writing never does.

## Why This Structure Exists
Almost every Python library you will use in AI work (models, tokenizers, API clients) is a class with `__init__` and methods. The shared-mutable-attribute bug is a real source of cross-request data leaks in web services and agents, so knowing it early saves debugging time.
