# `_5_AbstractClasses.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
An abstract class is a base class that cannot be instantiated because it declares one or more `@abstractmethod`s that subclasses must implement. In Python you get this by inheriting from `abc.ABC` and decorating the required methods. It defines a contract and can still hold shared concrete code.

The enforcement happens at instantiation time: creating an object of a class that still has unimplemented abstract methods raises `TypeError`.

## Full Line-by-Line Breakdown

### SECTION 1: AN ABSTRACT BASE CLASS
`Shape` inherits `ABC` and marks `area()` abstract, while `describe()` is a normal method that calls `area()`. `Circle` implements `area()`, so `Circle(2).describe()` works and uses the shared `describe` from the base.

Output from a real run:

```text
===== SECTION 1: AN ABSTRACT BASE CLASS =====
Circle with area 12.57
```

### SECTION 2: INSTANTIATION FAILS
`Shape("x")` raises `TypeError` because the abstract method is unimplemented. The metaclass `ABCMeta` records the unimplemented names in `Shape.__abstractmethods__`; `object.__new__` refuses to build an instance while that set is non-empty.

Output from a real run:

```text
===== SECTION 2: INSTANTIATION FAILS =====
TypeError: Can't instantiate abstract class Shape without an implementation for abstract method 'area'
Shape.__abstractmethods__: {'area'}
```

### SECTION 3: TRAP - INCOMPLETE SUBCLASS
`Lazy` extends `Shape` but forgets `area`, so it is still abstract and the error message names the missing method. `Fixed` implements it and instantiates fine. Note the error is raised when you create the object, not when you define the class.

Output from a real run:

```text
===== SECTION 3: TRAP - INCOMPLETE SUBCLASS =====
TypeError: Can't instantiate abstract class Lazy without an implementation for abstract method 'area'
After implementing area(): fixed with area 1.00
```

### SECTION 4: TRAP - FORGETTING ABC
Without `ABC` (or `metaclass=ABCMeta`) the `@abstractmethod` decorator is just a marker and nothing stops instantiation. A very common silent mistake.

Output from a real run:

```text
===== SECTION 4: TRAP - FORGETTING ABC =====
Instantiated fine: NotReallyAbstract
Enforcement comes from the ABCMeta metaclass, not the decorator alone.
```

### SECTION 5: ABSTRACT METHODS CAN HAVE CODE
An abstract method may contain a body, which subclasses can reuse via `super()`. They are still required to override it, which is something Java does not allow for abstract methods.

Output from a real run:

```text
===== SECTION 5: ABSTRACT METHODS CAN HAVE CODE =====
[base] shared prefix work, then: hello
[console] hello
```

### SECTION 6: ABSTRACT PROPERTY AND register
Combine `@property` above `@abstractmethod` to require a property. `Named.register(Foreign)` makes `Foreign` a virtual subclass: `isinstance` returns `True` even though it does not inherit, which fits the duck typing philosophy.

Output from a real run:

```text
===== SECTION 6: ABSTRACT PROPERTY AND register =====
Tag().label: tag-1
isinstance(Tag(), Named): True
isinstance(Foreign(), Named) after register: True
```

## Key Differences From Java
| Java | Python |
|---|---|
| `abstract class Shape { abstract double area(); }` | `class Shape(ABC)` with `@abstractmethod` |
| Compile-time error on `new Shape()` | `TypeError` at runtime when instantiating |
| Abstract methods have no body | May have a body, callable with `super()` |
| `interface` is a separate construct | No interface keyword: use ABCs or `Protocol` |
| Missing implementation caught by the compiler | Caught when the object is created |
| Subclass must declare inheritance | `ABC.register` allows virtual subclasses |

## Key Rules / Gotchas Recap
- Inherit from `ABC` or the decorator is decorative only.
- Instantiation fails until every abstract method is overridden.
- The check is at instantiation, not at class definition.
- Use ABCs when you want shared code plus a mandatory contract; use `Protocol` for pure shape checking.
- You can require abstract properties, class methods and static methods too.

## Why This Structure Exists
Plugin systems, model backends and tool interfaces in agents use ABCs so that a missing method fails immediately and loudly instead of deep inside a run.
