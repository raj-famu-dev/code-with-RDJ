# `_2_VariablesAndDataTypes.py`

## Concept
Declaring variables under Python's dynamic typing system — no type declarations, runtime type inference, and the ability to reassign a variable to a completely different type.

## The Full Code

```python
my_int = 2_000_000
my_big_int = 15000000000
my_float = 5.75
my_name = "RDJ"
greeting_quote = 'Hello'
is_python_fun = True
is_learning_done = False

print(type(my_int))
print(type(my_float))
print(type(my_name))
print(type(is_python_fun))

flexible_variable = 42
print(flexible_variable, type(flexible_variable))
flexible_variable = "Now I'm a string!"
print(flexible_variable, type(flexible_variable))
flexible_variable = 3.14
print(flexible_variable, type(flexible_variable))

age = 25
greeting = "Age: " + str(age)
print(greeting)

PI = 3.14159
MAX_USERS = 100
print("Constant PI:", PI)
PI = 3.14
print("PI after 'illegal' reassignment:", PI)

student_age = 21
print("Student age:", student_age)

x, y, z = 1, 2, 3
print(x, y, z)

a = b = c = 0
print(a, b, c)
```

## Line-by-Line Breakdown

### `my_int = 2_000_000`
No type keyword anywhere — Python looks at the value `2_000_000` and infers it's an `int`. The underscores are purely visual separators, identical in purpose to Java's.

### `my_big_int = 15000000000`
No `L` suffix needed at all. Python has only **one** integer type with no fixed size — there's no `byte`/`short`/`int`/`long` distinction to worry about, and no overflow risk regardless of how large the number grows.

### `my_float = 5.75`
No `f` suffix required. Python has only **one** floating-point type — there's no separate `float` vs `double` the way Java has.

### `greeting_quote = 'Hello'`
Single quotes work identically to double quotes for strings — Python makes no distinction between them at all.

### `is_python_fun = True`
Booleans are capitalized: `True`/`False`, not `true`/`false`.

### `type(my_int)`, etc.
`type()` is a built-in function that reports a variable's **current** type at runtime — since Python never declares types upfront, this is the tool used to inspect what something actually is right now.

### `flexible_variable = 42` → reassigned to a String → reassigned to a float
This is the core demonstration of **dynamic typing**: the same variable name holds an `int`, then a `str`, then a `float`, with zero errors. In Java, declaring `int flexibleVariable = 42;` would make any later attempt to assign a String to it a **compile error**. Python allows this because types are checked only at runtime, never ahead of time.

### `greeting = "Age: " + str(age)`
Python does **not** auto-convert numbers when concatenating with `+` — unlike Java, which silently converts `age` into text. Here, `str(age)` performs that conversion explicitly; omitting it would crash with a `TypeError`.

### `PI = 3.14159` then `PI = 3.14`
Python has **no `final` keyword at all**. The `ALL_CAPS` naming convention (`PI`, `MAX_USERS`) is purely a signal to other developers — "please don't reassign this" — but the language itself places zero restriction on actually doing so.

### `student_age = 21`
Demonstrates `snake_case`, the dominant Python naming convention for variables — contrasted with Java's `camelCase`.

### `x, y, z = 1, 2, 3`
**Multiple assignment** — Python lets you assign several variables in a single line, with no equivalent syntax in Java at all.

### `a = b = c = 0`
Assigns the **same** value to three variables in one statement — also unique to Python's syntax flexibility here.

## Key Differences From Java

| Concept | Java | Python |
|---|---|---|
| Type declaration | `int x = 5;` — required, locked forever | `x = 5` — inferred, can change later |
| Number of integer types | 4 (`byte`, `short`, `int`, `long`) | 1 (`int`), with no size limit or overflow |
| Number of float types | 2 (`float`, `double`) | 1 (`float`) |
| Boolean literals | `true` / `false` | `True` / `False` |
| Checking a variable's type | Known at compile time | `type(variable)` at runtime |
| Reassigning to a different type | Compile error | Fully allowed |
| String + number concatenation | Auto-converts | Crashes — requires explicit `str()` |
| Constants | `final` keyword, compiler-enforced | No language feature — pure naming convention |
| Naming convention | camelCase | snake_case |
| Multiple assignment in one line | Not supported | `x, y, z = 1, 2, 3` |

## Key Rules / Gotchas Recap

- A variable can hold any type and be freely reassigned to a different type later — Python never locks a variable to its first assigned type
- `+` between a string and a number always crashes — explicit `str()` conversion is mandatory, no exceptions
- `final`/constant protection does not exist at the language level — it's a human convention only

## Why This Structure Exists

Python is dynamically typed, meaning the interpreter checks types only when a line actually executes, never ahead of time the way Java's compiler does. This trades away an entire category of compile-time safety for flexibility and less upfront ceremony — but it also means type-related bugs (like mixing a string and a number) only ever surface when that specific line of code actually runs, not before.