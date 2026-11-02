# `_3_Inheritance.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Inheritance lets a class reuse and specialise another class: `class Dog(Animal)`. You override a method by defining one with the same name, and call the parent's version with `super()`. Python also allows multiple inheritance, so it needs a rule for which class wins; that rule is the method resolution order (MRO), computed with the C3 algorithm.

The important correction for Java programmers: `super()` does not mean "my parent". It means "the next class in the MRO".

## Full Line-by-Line Breakdown

### SECTION 1: BASIC INHERITANCE AND OVERRIDING
`Dog` and `Puppy` override `speak`. `describe` is defined once in `Animal` and calls `self.speak()`, so each object uses its own version (that is runtime polymorphism). `Puppy.__init__` calls `super().__init__(name)` explicitly to initialise the parent part, and `Puppy.speak` extends the parent behaviour with `super().speak()`. `isinstance` and `issubclass` follow the inheritance chain.

Output from a real run:

```text
===== SECTION 1: BASIC INHERITANCE AND OVERRIDING =====
[Animal] Generic makes a sound
[Dog] Rex barks
[Puppy] Bit barks squeakily
isinstance(Puppy, Animal): True
issubclass(Puppy, Dog): True
```

### SECTION 2: TRAP - FORGETTING super().__init__
Java inserts an implicit call to the parent constructor. Python does not. `ForgetfulDog.__init__` never runs `Animal.__init__`, so `self.name` is never created and `speak()` fails with `AttributeError` at use time, not at construction.

Output from a real run:

```text
===== SECTION 2: TRAP - FORGETTING super().__init__ =====
AttributeError: 'ForgetfulDog' object has no attribute 'name'
```

### SECTION 3: MULTIPLE INHERITANCE AND THE MRO
`D(B, C)` where both `B` and `C` derive from `A` is the diamond. `D.__mro__` is `D, B, C, A, object`: every class appears once, children before parents, and the left-to-right order of bases is respected. Each `who()` calls `super().who()`, so the chain `D>B>C>A` runs through every class exactly once.

Output from a real run:

```text
===== SECTION 3: MULTIPLE INHERITANCE AND THE MRO =====
D().who(): D>B>C>A
D.__mro__: ['D', 'B', 'C', 'A', 'object']
A appears once, last: the diamond is solved by C3 linearization.
```

### SECTION 4: super() IS NEXT-IN-MRO
Inside `B`, `super()` goes to `A` when you have a `B` object, but to `C` when the object is a `D`, because it uses the MRO of the object's actual class. Reordering the bases (`E(C, B)`) changes the MRO and therefore the result (`C>B>A`). Base class order is part of your design.

Output from a real run:

```text
===== SECTION 4: super() IS NEXT-IN-MRO =====
B().who(): B>A (B alone: next is A)
In D, B's super() goes to C, not A. Order of bases matters.
E.__mro__: ['E', 'C', 'B', 'A', 'object']
E().who(): C>B>A
```

### SECTION 5: MIXINS
A mixin is a small class that adds one capability and is not meant to stand alone. `JsonMixin.to_json` works for any class that has instance attributes. This is the idiomatic Python substitute for Java default methods on interfaces.

Output from a real run:

```text
===== SECTION 5: MIXINS =====
{"name": "raj", "level": 3}
```

### SECTION 6: MRO CONFLICT ERROR
If the base order contradicts the hierarchy (listing `A` before its own subclass `D`) Python cannot build a consistent order and raises `TypeError` when the class is defined, not later.

Output from a real run:

```text
===== SECTION 6: MRO CONFLICT ERROR =====
TypeError: Cannot create a consistent method resolution order (MRO) for bases A, D
```

## Key Differences From Java
| Java | Python |
|---|---|
| `class Dog extends Animal` | `class Dog(Animal)` |
| Implicit `super()` constructor call | You must call `super().__init__(...)` yourself |
| `@Override` annotation (checked) | No annotation needed; a typo in the name silently creates a new method (use `typing.override` on 3.12+ with a type checker) |
| Single class inheritance; many interfaces | Multiple class inheritance allowed |
| `super.method()` = parent | `super().method()` = next class in the MRO |
| Methods overridable unless `final` | Everything overridable; no `final` |
| Diamond problem avoided by banning it | Diamond solved by C3 linearization |

## Key Rules / Gotchas Recap
- Call `super().__init__()` in every `__init__` unless you deliberately skip it.
- `D.__mro__` (or `D.mro()`) shows the lookup order; read it when behaviour surprises you.
- Cooperative multiple inheritance needs every class to call `super()`.
- Prefer composition or small mixins over deep hierarchies.
- Overriding is by name only: there is no overloading by parameter types.

## Why This Structure Exists
Frameworks such as Django and many ML libraries are built on class hierarchies and mixins, and you extend them by subclassing. Debugging a wrong method being called usually means reading the MRO.
