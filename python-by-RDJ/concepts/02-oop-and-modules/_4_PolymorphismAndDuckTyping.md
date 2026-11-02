# `_4_PolymorphismAndDuckTyping.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Duck typing means Python cares about what an object can DO, not what class it is: if it has a `speak()` method, you can call `speak()`. Polymorphism therefore does not require a shared base class or interface. `typing.Protocol` adds optional, checkable structure on top: you describe the methods you need, and a type checker verifies any object that has them, again without inheritance.

The trade-off is that plain duck typing only fails at runtime, so Protocols plus a type checker give you much of what Java interfaces give at compile time.

## Full Line-by-Line Breakdown

### SECTION 1: DUCK TYPING
`Duck` and `Robot` are unrelated classes that both define `speak()`. `make_noise` takes anything and calls `speak()`. Both work; no interface was declared.

Output from a real run:

```text
===== SECTION 1: DUCK TYPING =====
Duck -> Quack
Robot -> Beep
```

### SECTION 2: TRAP - FAILS AT CALL TIME
Passing `42` is accepted by the language, and the error appears only when `thing.speak()` runs: `AttributeError`. There is no compiler step to catch it. In a rarely executed branch this can hide for a long time.

Output from a real run:

```text
===== SECTION 2: TRAP - FAILS AT CALL TIME =====
AttributeError: 'int' object has no attribute 'speak'
No compiler to catch this: that is what Protocol + a type checker add.
```

### SECTION 3: PROTOCOL
`Speaker` is a Protocol: it lists `speak() -> str`. `announce(s: Speaker)` documents and (with mypy or pyright) enforces that argument shape. `Duck` and `Robot` never mention `Speaker`; matching the shape is enough. This is called structural typing, in contrast to Java's nominal typing where a class must say `implements`. Python itself does not check these hints when running.

Output from a real run:

```text
===== SECTION 3: PROTOCOL =====
Announcing: Quack
Announcing: Beep
```

### SECTION 4: isinstance WITH A PROTOCOL
Adding `@runtime_checkable` lets `isinstance` work with a Protocol. It only checks that the attribute NAME exists, not its signature or type, so `FakeSpeaker` (where `speak` is a string) passes. Use runtime checks sparingly and rely on the static checker for real verification.

Output from a real run:

```text
===== SECTION 4: isinstance WITH A PROTOCOL =====
isinstance(Duck(), Speaker): True
isinstance(42, Speaker): False
isinstance(FakeSpeaker(), Speaker): True (only checks the NAME exists, not the signature)
```

### SECTION 5: POLYMORPHIC LOOP
`Square` and `Rect` both have `area()`. `total_area` accepts a list of anything matching the `Shape` Protocol and sums the areas. The result `16` is `4 + 12`. No common parent class is needed.

Output from a real run:

```text
===== SECTION 5: POLYMORPHIC LOOP =====
total area: 16
```

### SECTION 6: BUILT-INS ARE DUCK TYPED
`len()` works on any object with `__len__`, and truthiness uses `__len__` when `__bool__` is absent. The language's own protocols (iteration, `with`, `len`, indexing) are all duck typed in the same way, which is why implementing dunder methods makes your classes feel built-in.

Output from a real run:

```text
===== SECTION 6: BUILT-IN DUCK TYPING =====
len(Countdown(5)): 5 (len() just needs __len__)
bool(Countdown(0)): False (falsy because __len__ is 0)
```

## Key Differences From Java
| Java | Python |
|---|---|
| Polymorphism through `interface`/`abstract class`; class must declare `implements` | Any object with the right methods works; no declaration |
| Compile-time error if a method is missing | `AttributeError` at runtime (or a type checker error with Protocol) |
| Nominal typing | Duck typing (runtime) and structural typing (`Protocol`, static) |
| `instanceof Interface` always reliable | `isinstance` with a Protocol needs `@runtime_checkable` and checks names only |
| Generics with bounds (`<T extends Comparable<T>>`) | `Protocol` or `TypeVar(bound=...)` |
| Interfaces can add default methods | Protocols describe shape only; share code with base classes or mixins |

## Key Rules / Gotchas Recap
- Code against behaviour, not class names.
- Avoid `type(x) == Foo`; prefer duck typing or `isinstance` when you must check.
- Protocols are for static checkers; Python never enforces annotations at runtime.
- `@runtime_checkable` isinstance checks existence only.
- Test with unusual objects (fakes, mocks) to prove your function really only needs the Protocol.

## Why This Structure Exists
Duck typing is why a test double, a mock model client and the real API client can be swapped freely in AI pipelines. Protocols let you define "anything that looks like an LLM client" once and keep the code checkable.
