# `_2_Encapsulation.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Python has no `private` keyword. Instead it relies on naming conventions: a leading underscore means "internal, please do not touch", and a double leading underscore triggers name mangling to avoid accidental clashes in subclasses. When you need validation or computed values, `@property` lets you keep a plain attribute-style API (`obj.x`) while running code behind it.

The key mindset is "we are all consenting adults": the language will not stop a determined caller, so design for clarity, not enforcement.

## Full Line-by-Line Breakdown

### SECTION 1: UNDERSCORE CONVENTIONS
`owner` is public. `_balance` has one underscore: it is fully accessible, the underscore is a message to other programmers (and linters) that it is internal. `__pin` has two leading underscores and no trailing ones, so Python renames it. Accessing `acct.__pin` from outside raises `AttributeError`, but not because it is secret; the stored name is different.

Output from a real run:

```text
===== SECTION 1: UNDERSCORE CONVENTIONS =====
public acct.owner: Raj
single underscore still reachable: 0
acct.__pin -> AttributeError: 'Account' object has no attribute '__pin'
```

### SECTION 2: NAME MANGLING IS NOT SECURITY
`vars(acct)` reveals the real name, `_Account__pin`, which is `_ClassName__attr`. Anyone can read it. Never use mangling to protect passwords or tokens. Inside the class, `self.__pin` is silently rewritten to `self._Account__pin`, which is why `pin_matches` still works.

Output from a real run:

```text
===== SECTION 2: NAME MANGLING IS NOT SECURITY =====
vars: ['_Account__pin', '_balance', 'owner']
acct._Account__pin: 1234
pin_matches('1234'): True
```

### SECTION 3: MANGLING AVOIDS SUBCLASS COLLISIONS
Mangling exists so a subclass can pick the same attribute name as its parent without overwriting it. `Base` stores `_Base__secret` and `Child` stores `_Child__secret`; both exist side by side, and `base_secret()` still returns `base`. This is the real purpose of the feature.

Output from a real run:

```text
===== SECTION 3: MANGLING AVOIDS SUBCLASS COLLISIONS =====
base_secret(): base
vars: ['_Base__secret', '_Child__secret']
```

### SECTION 4: PLAIN ATTRIBUTES FIRST
Java habit says every field needs `getX()`/`setX()`. In Python start with a plain public attribute. If you later need validation, switch to a property under the same name and no caller changes. That is why Python code rarely has trivial getters and setters.

Output from a real run:

```text
===== SECTION 4: PLAIN ATTRIBUTES FIRST =====
p.x: 2.5
You can add validation LATER with @property without changing callers.
```

### SECTION 5: @PROPERTY WITH VALIDATION
`@property def celsius` is the getter; `@celsius.setter` is the setter. The data lives in `_celsius`, the property name is `celsius`. In `__init__`, `self.celsius = celsius` goes through the setter, so the constructor is validated too. `fahrenheit` has only a getter, so it is computed and read-only; assigning to it raises `AttributeError`.

Output from a real run:

```text
===== SECTION 5: @PROPERTY WITH VALIDATION =====
celsius: 100 | fahrenheit: 212.0
after set 0 -> fahrenheit: 32.0
setter rejected: below absolute zero
constructor also validated: below absolute zero
read-only property: property 'fahrenheit' of 'Temperature' object has no setter
```

### SECTION 6: TRAP - PROPERTY RECURSION
If the getter reads the property by its own name (`self.v`) it calls itself forever and ends in `RecursionError`. Store the value under a different name, conventionally with a leading underscore (`self._v`).

Output from a real run:

```text
===== SECTION 6: TRAP - PROPERTY RECURSION =====
RecursionError: property returned itself instead of self._v
```

### SECTION 7: DELETER
`@nick.deleter` runs when you write `del pr.nick`. It is rarely needed but completes the property trio (get, set, delete). Here it prints a message and resets the stored value.

Output from a real run:

```text
===== SECTION 7: DELETER =====
deleting nick
nick now: None
```

## Key Differences From Java
| Java | Python |
|---|---|
| `private`, `protected`, `public`, package-private enforced by the compiler/JVM | Conventions: `_x` internal, `__x` mangled, no enforcement |
| Getters/setters on every field from day one | Plain attributes; add `@property` only when you need logic |
| `getFahrenheit()` method call | `t.fahrenheit` looks like an attribute but runs code |
| Reflection with `setAccessible(true)` needed to break privacy | `obj._Account__pin` works with no tricks |
| `final` fields | No `final`; use properties without a setter, `frozen` dataclasses, or convention |

## Key Rules / Gotchas Recap
- One underscore: internal by convention only.
- Two leading underscores (not ending in two): renamed to `_Class__name`; for subclass safety, NOT secrecy.
- Dunder names like `__init__` (two on both sides) are never mangled.
- Properties need the getter defined first; the setter uses `@name.setter`.
- The getter must read a differently named attribute or it recurses infinitely.
- Do not store real secrets in objects expecting privacy; Python cannot hide memory from the code in the same process.

## Why This Structure Exists
Libraries expose a clean public API and keep internals underscored so they can change them later; reading `_private` names in someone else's code is a signal you are depending on something unstable. In security tooling, knowing that Python privacy is cosmetic matters when you assess what untrusted code in the same process could read.
