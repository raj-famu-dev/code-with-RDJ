# `_9_Functions.py`

## Concept
Standalone functions with no declared types, no method overloading at all, and native default-parameter/`*args`/`**kwargs` support replacing what Java needs overloading to simulate.

## The Full Code

```python
def greet_user():
    print("Welcome to Python Functions!")
greet_user()

def greet_by_name(user_name):
    print(f"Hello, {user_name}!")
greet_by_name("RDJ")

def add_numbers(a, b):
    return a + b
total = add_numbers(5, 10)

def calculate_average(a, b, c):
    return (a + b + c) / 3
average = calculate_average(85, 92, 78)

def greet_with_default(user_name, greeting="Hello"):
    print(f"{greeting}, {user_name}!")
greet_with_default("RDJ")
greet_with_default("RDJ", "Welcome back")

def add(a, b):
    return a + b
def add(a, b, c):
    return a + b + c
print(add(1, 2, 3))

def print_profile(name, age, is_active):
    print(f"Name: {name}, Age: {age}, Active: {is_active}")
print_profile("RDJ", 25, True)
print_profile(age=30, name="Dana", is_active=False)
print_profile("Charlie", is_active=True, age=19)

def sum_all(*nums):
    total = 0
    for n in nums:
        total += n
    return total
print(sum_all(1, 2, 3, 4, 5))

def print_details(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")
print_details(name="RDJ", age=25, city="Austin")

def print_message(msg):
    print(msg)
result = print_message("This prints something")
print(result)

def build_message(msg):
    return f"Built message: {msg}"

def modify_value(value):
    value = value + 100
original_number = 10
modify_value(original_number)
print(original_number)

def modify_list(lst):
    lst[0] = 999
numbers = [1, 2, 3]
modify_list(numbers)
print(numbers[0])

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def add_with_hints(a: int, b: int) -> int:
    return a + b
print(add_with_hints("3", "4"))
```

## Line-by-Line Breakdown

### `def greet_user(): ... greet_user()`
`def` is Python's function-definition keyword — no `static`, no return type, no class required to contain it at all. The function stands completely on its own.

### `def greet_by_name(user_name):`
No type declared on the parameter at all — Python accepts whatever is passed in, checked only if and when the code inside actually uses it in a type-sensitive way.

### `return a + b`
`return` works conceptually the same as Java, but notice there's **no return type anywhere in the function signature** — Python figures out what's being returned purely by what the `return` statement evaluates to at runtime.

### `def greet_with_default(user_name, greeting="Hello"):`
**Default parameter values are a native Python feature.** Calling `greet_with_default("RDJ")` uses `"Hello"` automatically; calling it with a second argument overrides that default. Java has no equivalent syntax at all — this exact scenario would require two separate overloaded methods in Java.

### `def add(a, b): ...` followed immediately by `def add(a, b, c): ...`
**This demonstrates that Python has no method overloading whatsoever.** The second `def add` doesn't create an additional overload — it **completely replaces** the first. After this point, calling `add(2, 3)` would crash with a missing-argument error, since only the 3-parameter version exists anymore. This is a fundamental difference from Java, where multiple same-named methods can coexist as long as their parameter signatures differ.

### `print_profile(age=30, name="Dana", is_active=False)`
**Keyword arguments** — calling a function by naming each parameter explicitly, in any order, regardless of how the function was originally defined. Java has no equivalent to this at all; Java method calls are always strictly positional.

### `def sum_all(*nums): ... for n in nums: ...`
The `*` before `nums` collects any number of extra positional arguments into a **tuple**. This is conceptually similar to Java's varargs (`int... nums`), but Python's version isn't locked to one declared type — any mix of argument types could technically be passed in.

### `def print_details(**kwargs): ... for key, value in kwargs.items():`
The `**` before `kwargs` collects any number of **named** arguments into a dictionary. This has no Java equivalent at all — there's no way in Java to accept an arbitrary, unplanned set of named parameters.

### `result = print_message("This prints something")` → `print(result)` → `None`
`print_message` has **no explicit `return` statement**. Python has no `void` keyword at all — a function with no return statement automatically returns a special value called `None` (Python's version of `null`).

### `def modify_value(value): value = value + 100`
Reassigning the parameter inside the function only changes the **local** name — `original_number` outside remains `10` afterward. This mirrors Java's pass-by-value behavior for primitives exactly.

### `def modify_list(lst): lst[0] = 999`
This **does** persist outside the function — `numbers[0]` becomes `999` after the call. The underlying reason is identical to Java arrays: both `numbers` and the parameter `lst` reference the **same** list object in memory, so modifying its *contents* (not reassigning the whole parameter) is visible everywhere that object is referenced.

### `def factorial(n): if n <= 1: return 1 ...`
Recursion works the same way conceptually as Java — a base case to stop, a recursive case that calls itself with a smaller input. No return type declaration needed anywhere.

### `def add_with_hints(a: int, b: int) -> int:` then called with `"3"`, `"4"`
**Type hints look like Java's type declarations but are purely decorative.** The function signature suggests `int` parameters and an `int` return, but calling it with strings instead works anyway — Python concatenates `"3"` and `"4"` into `"34"` without complaint. Type hints exist for human readers and IDE tooling (autocomplete, static analysis), but the Python interpreter itself never enforces them at runtime.

## Key Differences From Java

| Concept | Java | Python |
|---|---|---|
| Keyword | Lives inside a class, often `static` | `def` — standalone, no class required |
| Return type | Declared, enforced by the compiler | Never declared; type hints are optional and unenforced |
| `void` | A real keyword | **Doesn't exist** — no return statement gives `None` |
| Method overloading | Fully supported | **Doesn't exist** — a same-named `def` replaces the previous one entirely |
| Default parameter values | Not supported — requires overloading | Native feature |
| Calling by parameter name | Not supported — strictly positional | Fully supported — keyword arguments, any order |
| Varargs | `int... nums` — one type only | `*args` — any type, collected into a tuple |
| Named variable arguments | No equivalent | `**kwargs` — collected into a dict |
| Pass-by-value, primitives | Always | Same behavior for immutable types |
| Pass-by-value, objects/arrays | Reference copied, contents mutable | Identical behavior for mutable types (lists, dicts) |

## Key Rules / Gotchas Recap

- Defining two functions with the same name doesn't overload anything — the second silently replaces the first
- Type hints (`a: int`) are purely documentation — never enforced, unlike Java's compiler-checked parameter types
- Reassigning a parameter inside a function never affects the caller; modifying a mutable object's contents (like a list element) does

## Why This Structure Exists

Without method overloading, Python relies on default parameter values and `*args`/`**kwargs` to handle the same flexibility Java achieves with multiple overloaded signatures — this requires a genuinely different design instinct: instead of writing several similarly-named functions for different argument counts, you write **one** flexible function that adapts to whatever's passed in.