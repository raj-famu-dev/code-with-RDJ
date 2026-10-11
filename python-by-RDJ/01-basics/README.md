# 🐍 Python 01 — Basics

> Mirrors the Java `01-basics` curriculum topic-for-topic. Each section explains the Python code and calls out exactly how it differs from the equivalent Java concept.

![Language](https://img.shields.io/badge/Language-Python%203.15-blue)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Type](https://img.shields.io/badge/Type-Concept%20Practice-yellow)

---

## 📌 About This Folder

This is the Python companion to `java-mastery-lab`'s `01-basics` — same 11 topics, same order, same learning goals. The point isn't just to learn Python in isolation, but to learn it **relative to Java**, so every concept reinforces understanding of both languages at once.

---

## ✅ Progress Tracker

| # | File | Concept | Status |
|---|------|---------|:---:|
| 1 | `_1_HelloWorld.py` | Program structure & output | ✅ |
| 2 | `_2_VariablesAndDataTypes.py` | Variables & dynamic typing | ✅ |
| 3 | `_3_Operators.py` | Arithmetic, logical, membership, identity ops | ✅ |
| 4 | `_4_TypeCasting.py` | Type conversion functions | ✅ |
| 5 | `_5_ControlFlow.py` | if/elif/else, match-case | ✅ |
| 6 | `_6_Loops.py` | for, while, no do-while | ✅ |
| 7 | `_7_ListsAndArrays.py` | Lists, slicing, tuples | ✅ |
| 8 | `_8_Strings.py` | String methods & immutability | ✅ |
| 9 | `_9_Functions.py` | def, *args, **kwargs | ✅ |
| 10 | `_10_UserInput.py` | input() | ✅ |
| 11 | `_11_OutputFormatting.py` | f-strings | ✅ |

---

## 🗂 Concept Log

### 1️⃣ `_1_HelloWorld.py`

```python
print("Hello, RDJ is coding in Python!")

def greet():
    print("This only runs when the file is executed directly.")

if __name__ == "__main__":
    greet()
```

**What the code does:** `print()` runs immediately — there's no wrapping class or entry-point method required at all. The `if __name__ == "__main__":` block is Python's closest equivalent to Java's `main()`, but it's a **convention**, not a requirement — `__name__` is a special built-in variable that Python sets to `"__main__"` only when the file is run directly, and to the module's name if it's imported elsewhere instead.

**How this differs from Java:**
| Java | Python |
|---|---|
| `public class ClassName { public static void main(String[] args) { ... } }` is mandatory | No class or entry-point method required at all — code runs top to bottom |
| File name must match the public class name | No such requirement |
| Semicolons end every statement | Line breaks end statements |
| `main()` is enforced by the JVM | `if __name__ == "__main__":` is optional, used only when a file might later be imported |

---

### 2️⃣ `_2_VariablesAndDataTypes.py`

```python
my_int = 2_000_000
my_big_int = 15000000000
my_float = 5.75
my_name = "RDJ"
is_python_fun = True

print(type(my_int))

flexible_variable = 42
flexible_variable = "Now I'm a string!"   # legal — no type lock-in at all

age = 25
greeting = "Age: " + str(age)   # str() required — no auto-conversion with +

PI = 3.14159
PI = 3.14   # Python allows this — 'final' doesn't exist
```

**What the code does:** Variables are never declared with a type — Python infers it from whatever value is assigned, and `type(variable)` checks it at runtime. Critically, the **same variable name can be reassigned to a completely different type** later in the program — something Java's compiler would reject outright. String concatenation with `+` requires explicit `str()` conversion for numbers, since Python (unlike Java) does **not** auto-convert non-string types when using `+`.

**How this differs from Java:**
| Java | Python |
|---|---|
| `int x = 5;` — type declared, locked forever | `x = 5` — type inferred, can change later |
| 8 distinct primitive types (`byte`, `short`, `int`, `long`, `float`, `double`, `char`, `boolean`) | Just `int`, `float`, `str`, `bool` — no size-based subtypes, no overflow |
| `boolean flag = true;` | `flag = True` (capitalized) |
| `"Age: " + age` auto-converts the number | `"Age: " + age` **crashes** — must use `str(age)` |
| `final` keyword enforced by compiler | No equivalent — `ALL_CAPS` is purely a naming convention, not enforced |
| camelCase convention | snake_case convention |

---

### 3️⃣ `_3_Operators.py`

```python
print(15 / 4)      # 3.75 — ALWAYS returns float
print(15 // 4)     # 3 — floor division, Java-style truncation equivalent
print(-15 // 4)    # -4 — floors toward negative infinity, NOT -3!
print(15 ** 2)     # 225 — built-in power operator

is_adult and has_id      # 'and', not &&
is_adult or has_id       # 'or', not ||
not is_adult              # 'not', not !

result = "Adult" if age >= 18 else "Minor"   # ternary-style expression

print('D' in "RDJ")        # membership operator — no Java equivalent
print(list1 is list2)      # identity operator — reference comparison
```

**What the code does:** `/` always returns a float in Python, even when dividing evenly — the reverse of Java's integer-truncation behavior. `//` gives Java-style truncated division, but **rounds toward negative infinity** for negatives, which disagrees with how `int()` truncates (toward zero) — a genuine internal inconsistency to watch for. Logical operators are spelled-out words (`and`/`or`/`not`) instead of symbols. The `in`/`not in` membership operators and `is`/`is not` identity operators have no Java equivalent at all.

**How this differs from Java:**
| Java | Python |
|---|---|
| `int / int` truncates automatically | `/` **always** returns float — use `//` for truncation |
| `Math.pow(a, 2)` | `a ** 2` — built-in operator |
| `x++`, `x--`, `++x`, `--x` | **Do not exist** — syntax error. Use `x += 1` |
| `&&`, `\|\|`, `!` | `and`, `or`, `not` |
| `condition ? a : b` | `a if condition else b` |
| `.contains()` / `.indexOf() != -1` | `in` / `not in` |
| `==` for object reference comparison | `is` / `is not` (since `==` checks content) |
| No chained comparisons | `1 < p < 15` works as a genuine combined check |

---

### 4️⃣ `_4_TypeCasting.py`

```python
truncated_price = int(9.99)     # 9 — truncates toward zero
parsed_int = int("123")
parsed_float = float("45.67")
number_as_string = str(42)

print(int(-9.99))    # -9 — truncates toward zero
print(-15 // 4)       # -4 — floors toward negative infinity (disagrees with int()!)

bool(0)       # False
bool('')      # False
bool(None)    # False
bool(-5)      # True — even negatives are "truthy"

letter = ord('A')    # 65 — replaces Java's (int) cast on a char
chr(65)              # 'A' — replaces Java's (char) cast on an int
```

**What the code does:** Conversion uses explicit functions (`int()`, `float()`, `str()`) instead of Java's `(type)` cast syntax. There's no byte/short/int/long distinction at all — Python integers have **no fixed size and no overflow**, growing as large as needed automatically. Python introduces "truthiness" — `bool()` can convert almost anything, with `0`, `""`, and `None` all evaluating to `False`. Since there's no `char` type, `ord()`/`chr()` replace Java's int↔char casting.

**How this differs from Java:**
| Java | Python |
|---|---|
| `(int) someDouble` | `int(some_float)` — a function call |
| Narrowing can silently overflow (`(byte) 130` → `-126`) | **No overflow exists at all** — ints grow arbitrarily large |
| `NumberFormatException` on bad conversion | `ValueError` |
| No concept of "truthiness" — only `true`/`false` are boolean | `bool()` works on almost any value, governed by truthiness rules |
| `(char)`/`(int)` casts for characters | `ord()` / `chr()` functions |
| `(int)` and integer division agree on direction | `int()` truncates toward zero, but `//` floors toward negative infinity — **they disagree** |

---

### 5️⃣ `_5_ControlFlow.py`

```python
if temperature > 30:
    print("It's hot outside.")
elif score >= 80:
    print("Grade: B")
else:
    print("Grade: F")

match day_number:
    case 1:
        day_name = "Monday"
    case _:
        day_name = "Invalid day number"
```

**What the code does:** Blocks are defined purely by **indentation** — there are no curly braces anywhere in Python. Every conditional line must end in a colon. `elif` replaces Java's `else if`. `match`/`case` (Python 3.10+) replaces traditional switch statements, with `case _:` as the default/fallback and **no fall-through risk whatsoever** — unlike Java's traditional switch, there's no `break` to forget.

**How this differs from Java:**
| Java | Python |
|---|---|
| Curly braces `{ }` define blocks | **Indentation itself** defines blocks — not cosmetic, it's actual syntax |
| `else if` | `elif` |
| `switch`/`case`/`break`, risk of fall-through | `match`/`case`, **cannot fall through at all** |
| `case 1, 2, 3 ->` | `case 1 \| 2 \| 3:` |
| Assignment-in-condition is a compile error | **Syntax error** — the grammar itself forbids `=` inside a condition |
| Missing brace → mismatched block bug | Missing/inconsistent indentation → `IndentationError` |

---

### 6️⃣ `_6_Loops.py`

```python
for i in range(1, 6):        # Python's ONLY for-loop style — always iterates a sequence
    print(i)

count = 1
while count <= 5:
    count += 1

while True:                   # Python's do-while substitute — no dedicated syntax exists
    attempts += 1
    if attempts >= 15:
        break

for index, value in enumerate(names):   # get index + value together
    print(index, value)

for i in range(1, 4):
    for j in range(1, 4):
        if i == 2 and j == 2:
            found = True
            break
    if found:
        break   # manual flag — no labeled break exists in Python
```

**What the code does:** Python's `for` loop **only** iterates over sequences — there's no C-style counting loop at all; `range()` generates the counting sequence instead. There's no `do-while` loop — the standard workaround is `while True:` with a `break` inside. Getting both index and value during iteration needs `enumerate()`, since a plain for-each only gives you the value. Labeled breaks (exiting a specific outer loop by name) don't exist — the workaround is a manual flag variable or restructuring into a function with `return`.

**How this differs from Java:**
| Java | Python |
|---|---|
| `for(int i=0; i<5; i++)` | `for i in range(5):` |
| Enhanced for-each is a separate syntax | **The only** for-loop style that exists |
| `do { } while(condition);` | **Doesn't exist** — simulate with `while True:` + `break` |
| Indexed for loop gives index naturally | `enumerate(sequence)` needed for index + value together |
| `break outerLoop;` | **Doesn't exist** — use a flag variable or extract to a function |
| Can't iterate a String directly | Strings are directly iterable, same as lists |
| No `for...else` concept | `for...else` runs the `else` only if the loop never hit a `break` |

---

### 7️⃣ `_7_ListsAndArrays.py`

```python
scores = [90, 85, 78, 92, 88]      # dynamic size — no fixed length ever
mixed_list = [1, "two", 3.0, True]  # mixed types allowed in one list

fruits.append("Mango")
fruits.insert(1, "Blueberry")
fruits.remove("Banana")
popped = fruits.pop()

print(sum(scores), max(scores), min(scores), sorted(scores))

numbers_list[2:5]     # slicing — no Java equivalent
numbers_list[::-1]    # reverses the entire list instantly

coordinates = (10, 20)   # tuple — immutable, closest thing to a "locked" collection

squares = [x ** 2 for x in range(1, 6)]   # list comprehension
```

**What the code does:** Python's `list` replaces Java's array entirely for everyday use — it's dynamic-size by default, can hold mixed types, and has built-in methods for nearly everything (`sum()`, `max()`, `min()`, `sorted()`) that Java requires manual loops for. Slicing (`list[start:stop:step]`) is a major Python-only feature with no Java equivalent, capable of extracting ranges or even reversing a list in one expression (`[::-1]`). Tuples are Python's immutable alternative, conceptually closest to a locked-down list. List comprehensions build a new list in one line, replacing what Java needs a full loop plus repeated `.add()` calls to accomplish.

**How this differs from Java:**
| Java | Python |
|---|---|
| Arrays are fixed-size | Lists grow/shrink freely — `.append()`, `.insert()`, `.remove()`, `.pop()` |
| Arrays hold one declared type only | Lists freely mix types |
| `.length` property | `len(list)` function |
| No negative indexing | `list[-1]` gets the last element |
| Manual loops for sum/max/min | Built-in `sum()`, `max()`, `min()`, `sorted()` |
| No slicing at all | `list[a:b:step]` — extract ranges, reverse, skip elements |
| `ArrayIndexOutOfBoundsException` | `IndexError` |
| No immutable collection equivalent in common use | Tuples — immutable by design |
| Loop + `.add()` to build a filtered list | List comprehensions: `[expr for x in seq if cond]` |

---

### 8️⃣ `_8_Strings.py`

```python
str1 = "Java"
str2 = "Java"
print(str1 == str2)   # True — ALWAYS content comparison, no String Pool trap

sample.strip().upper()           # .strip() not .trim(), .upper() not .toUpperCase()
sentence.find("Python")          # .find() not .indexOf()
sentence[7:13]                   # slicing replaces substring()
"love" in sentence               # 'in' keyword replaces .contains()

" ".join(words)                  # joining called ON the separator — backwards from Java intuition
text[::-1]                       # reverses a string instantly
```

**What the code does:** Strings remain immutable, same as Java, but `==` **always** compares content — Python has no equivalent to Java's String Pool reference-comparison trap at all. Many familiar methods exist under different names (`.strip()`, `.upper()`, `.find()`), and several Java methods have no direct equivalent (`.equalsIgnoreCase()`, `.isEmpty()`, `.isBlank()`), replaced instead by manual comparisons or Python's truthiness rules. `.join()` is called on the separator rather than the list — the single most common "backwards from Java intuition" gotcha in this topic.

**How this differs from Java:**
| Java | Python |
|---|---|
| `==` compares references — String Pool trap | `==` **always** compares content |
| `.length()` | `len(string)` |
| `.trim()` | `.strip()` |
| `.charAt(i)` | Direct indexing: `string[i]` |
| `.substring(a, b)` | Slicing: `string[a:b]` |
| `.equalsIgnoreCase()` | **Doesn't exist** — `.lower()` both sides manually |
| `.isEmpty()` / `.isBlank()` | **Don't exist** — compare to `""` or use truthiness |
| `StringBuilder(...).reverse()` | `string[::-1]` |
| `String.join(sep, list)` | `sep.join(list)` — called on the separator |

---

### 9️⃣ `_9_Functions.py`

```python
def greet_by_name(user_name):     # no parameter type, no return type declared
    print(f"Hello, {user_name}!")

def greet_with_default(user_name, greeting="Hello"):   # default values — native feature
    print(f"{greeting}, {user_name}!")

def sum_all(*nums):     # *args — variable arguments, any type
    return sum(nums)

def print_details(**kwargs):   # **kwargs — variable named arguments
    for key, value in kwargs.items():
        print(key, value)

def modify_list(lst):
    lst[0] = 999   # mutates the actual list — same reference behavior as Java arrays
```

**What the code does:** Functions use `def`, with no declared parameter types and no declared return type — everything is checked only at runtime, if at all (type hints exist but are never enforced). There's **no method overloading** in Python at all — defining a second function with the same name completely replaces the first, rather than coexisting. Default parameter values and `*args`/`**kwargs` are the idiomatic Python replacements for what Java needs overloading to simulate. Pass-by-value behavior mirrors Java exactly in spirit: immutable types (int, str, float) behave like Java primitives, while mutable types (lists, dicts) behave like Java arrays/objects — modifying contents persists outside the function, reassigning the whole parameter does not.

**How this differs from Java:**
| Java | Python |
|---|---|
| Lives inside a class, needs `static` for class-level calls | Standalone — no class required at all |
| Return type declared, enforced | Never declared; type hints are optional and unenforced |
| `void` keyword | **Doesn't exist** — no return statement gives `None` automatically |
| Method overloading fully supported | **Doesn't exist** — a same-named `def` replaces the previous one entirely |
| No default parameter values | Native feature: `def f(a, b="default"):` |
| Call only by position | Call by position **or** by keyword name, in any order |
| `int... nums` — one type only | `*args` — any type, collected into a tuple |
| No equivalent | `**kwargs` — named arguments collected into a dict |

---

### 🔟 `_10_UserInput.py`

```python
user_name = input("Enter your name: ")   # prints prompt AND reads input, in one call
age = int(input("Enter your age: "))      # manual conversion — input() is ALWAYS a string

is_student = input("Are you a student? (yes/no): ").lower() in ("yes", "y")

try:
    favorite_number = int(input("Enter your favorite number: "))
except ValueError:
    print("That wasn't a valid number!")
```

**What the code does:** `input()` is a single built-in function requiring no import, no object creation, and no `.close()` cleanup — a dramatic simplification compared to Java's Scanner setup. Every single thing it returns is a string, with no exceptions — numbers, booleans, anything must be manually converted afterward. This also means **the entire `nextInt()`/`nextLine()` buffer bug category from Java simply does not exist** — there's no leftover newline, no buffer to clear. There's no built-in boolean parser either, but that flexibility lets you accept "yes"/"no" or any format you choose, rather than being locked into Java's rigid `true`/`false` literal requirement.

**How this differs from Java:**
| Java | Python |
|---|---|
| `import java.util.Scanner;` + object creation | Nothing — `input()` is built-in and ready |
| `.nextInt()` / `.nextDouble()` / `.nextBoolean()` | `input()` always returns a string — convert manually |
| The buffer/newline bug | **Does not exist at all** |
| `.hasNextInt()` validation check | No equivalent — use `try`/`except` around the conversion instead |
| `.close()` required | Nothing to close — no object was ever created |
| Rigid boolean parsing | Fully custom — accept any format you want |

---

### 1️⃣1️⃣ `_11_OutputFormatting.py`

```python
print(f"Name: {name}, Age: {age}, Salary: {salary}")   # f-strings — modern standard

print(f"2 decimals: {pi:.2f}")
print(f"[{42:<10d}]")        # left-align
print(f"[{'Hi':^10s}]")      # centered — no Java equivalent at all

for item, price in zip(items, prices):   # zip() pairs two lists together
    print(f"{item:<10} {price:>10.2f}")

raw_path = r"C:\Users\RDJ"   # raw string — disables escape sequences entirely

x = 42
print(f"{x=}")               # prints: x=42 — debugging shortcut, no Java equivalent
```

**What the code does:** f-strings (`f"..."`) are Python's modern formatting standard — embed any variable or expression directly inside `{ }`, with optional format specifiers after a colon for precision, width, and alignment. Unlike Java's `%f`, Python shows the **full actual precision** of a float by default rather than always defaulting to 6 decimals. Centering text (`^`) has no Java equivalent at all. `zip()` elegantly pairs two lists together for iteration, replacing manual indexed loops. Python's formatting history includes two older styles (`%`-formatting and `.format()`) you'll encounter in existing code, even though f-strings are preferred for anything new.

**How this differs from Java:**
| Java | Python |
|---|---|
| `printf`/`String.format` only | f-strings, plus two older legacy styles you'll still encounter |
| `%f` always shows 6 decimals by default | f-strings show full actual precision unless specified |
| No centering option | `{'text':^10}` centers |
| `System.err.println()` built in | `print(..., file=sys.stderr)` — requires `import sys` |
| No raw string literal | `r"C:\Users\RDJ"` — disables all escape processing |
| No debug-printing shortcut | `f"{x=}"` prints both the expression and its value |
| Manual indexed loop to pair two arrays | `zip(list1, list2)` |

---

## 🧠 Skills Demonstrated

- Fluency in Python's dynamically-typed syntax, contrasted directly against Java's static typing at every step
- Understanding of exactly where Java's safety nets (compile-time type checking, overflow protection, enforced method signatures) are absent in Python, and what replaces them
- Practical experience with Python-only features that have no Java equivalent: slicing, list comprehensions, `*args`/`**kwargs`, `zip()`, f-string debug specifiers, tuples
- The ability to translate a known concept (loops, conditionals, functions) into an unfamiliar language's idioms rather than just its syntax

---

## ➡️ Next Up

Python's `01-basics` is complete, mirroring Java's. Ready to move into Python's object-oriented programming concepts — classes, inheritance, and how Python's approach to OOP differs from Java's (no access modifiers enforced by the language, duck typing, and more).