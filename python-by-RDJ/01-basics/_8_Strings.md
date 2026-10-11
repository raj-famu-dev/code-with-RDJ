# `_8_Strings.py`

## Concept
String immutability (same as Java) paired with content-based `==` comparison (unlike Java), renamed methods throughout, and slicing replacing `substring()` entirely.

## The Full Code

```python
greeting = "Hello"
name = 'RDJ'

multiline = """This spans
multiple lines
without any escape characters."""

str1 = "Java"
str2 = "Java"
str3 = "Jav" + "a"
print(str1 == str2)
print(str1 == str3)

full_greeting = greeting + ", " + name + "!"

age = 25
combined = "Age: " + str(age)
print(f"Age: {age}")

original = "Hello"
modified = original + " World"

sample = "  Python Programming  "
print(len(sample))
print(sample.strip())
print(sample.strip().upper())
print(sample.strip().lower())

word = "Python"
print(word[0])

sentence = "I love Python programming"
print(sentence.find("Python"))
print(sentence.find("Java"))
print(sentence[7:])
print(sentence[7:13])
replaced = sentence.replace("Python", "Java")
print("love" in sentence)
print("PYTHON" == "python")
print("PYTHON".lower() == "python".lower())
print(sentence.startswith("I"))
print(sentence.endswith("programming"))

empty_str = ""
blank_str = "   "
print(empty_str == "")
print(blank_str.strip() == "")
print(not empty_str)

csv_data = "Alice,Bob,Charlie,Dave"
names_list = csv_data.split(",")

words = ["Python", "is", "fun"]
joined = " ".join(words)

for letter in "Python":
    print(letter)

text = "Hello World"
print(text[0:5])
print(text[6:])
print(text[::-1])

pieces = []
for i in range(1, 6):
    pieces.append(f"Number{i}")
result = " ".join(pieces)
```

## Line-by-Line Breakdown

### `greeting = "Hello"` / `name = 'RDJ'`
Single and double quotes are **completely interchangeable** in Python — unlike Java, where double quotes are mandatory for Strings.

### `multiline = """..."""`
Triple-quoted strings allow genuine multi-line text with no escape characters needed at all. Java only gained something similar (text blocks) in version 15+, and even then with stricter rules; Python has supported this since its earliest versions.

### `print(str1 == str2)` → `True`, `print(str1 == str3)` → `True`
**The biggest relief in this file.** In Python, `==` **always** compares content for strings, regardless of whether they're literals or built at runtime (`str3` is constructed via concatenation, not a literal). There is no equivalent to Java's String Pool trap, where `==` sometimes compares references instead of content.

### `combined = "Age: " + str(age)`
Recap from Topic 2's gotcha — concatenating a string and a number with `+` still crashes without explicit `str()` conversion. `f"Age: {age}"` sidesteps this entirely.

### `modified = original + " World"`
Confirms immutability — `original` remains `"Hello"` afterward; `+` always produces a **new** string, never modifies in place.

### `len(sample)` / `sample.strip()`
`len()` replaces `.length()`. `.strip()` replaces `.trim()` — removes leading/trailing whitespace, but notice the **method name itself is different**, not just the behavior.

### `sample.strip().upper()` / `.lower()`
`.upper()` and `.lower()` replace Java's `.toUpperCase()`/`.toLowerCase()` — again, same behavior, different names entirely.

### `word[0]`
Characters are accessed via **direct indexing** — there is no `.charAt()` method in Python at all; a string simply supports index access the same way a list does.

### `sentence.find("Python")` / `sentence.find("Java")` → `-1`
`.find()` replaces `.indexOf()`, returning `-1` on no match, same convention as Java. A related method, `.index()`, behaves similarly but **crashes** with a `ValueError` instead of returning `-1` — worth knowing both exist.

### `sentence[7:]` / `sentence[7:13]`
**Slicing fully replaces `.substring()`** — the end index is exclusive, matching Java's `substring(start, end)` convention exactly, just using bracket syntax instead of a method call.

### `"love" in sentence`
The `in` keyword (recap from Topic 3) replaces `.contains()` entirely.

### `"PYTHON" == "python"` → `False`; `.lower()` on both sides → `True`
String comparison is case-sensitive by default, same as Java. But Python has **no `.equalsIgnoreCase()` method at all** — the standard workaround is lowering both sides manually before comparing.

### `empty_str == ""` / `blank_str.strip() == ""` / `not empty_str`
Python has **no `.isEmpty()` or `.isBlank()` methods**. The idiomatic replacements: compare directly to `""`, or `.strip()` first for a blank-check, or lean on truthiness (`not empty_str` is `True` precisely because an empty string is "falsy," recap Topic 4).

### `csv_data.split(",")`
Behaves identically to Java's `.split()`.

### `" ".join(words)`
**This is the single most common "backwards from Java intuition" moment in Python strings.** `.join()` is called **on the separator**, not on the list — `" ".join(words)`, not `words.join(" ")`. It joins every element of the list using whatever string it's called on as the glue between them.

### `for letter in "Python":`
Strings are **directly iterable** — no conversion to a char array needed at all, unlike Java's `.toCharArray()` requirement.

### `text[::-1]`
Reverses an entire string in one slicing expression — Java needs `new StringBuilder(text).reverse().toString()` to accomplish the same thing.

### `pieces = []` → loop appending → `" ".join(pieces)`
The idiomatic Python replacement for Java's `StringBuilder` pattern: collect pieces in a list during the loop, then join them all at once at the end, rather than repeatedly concatenating strings directly.

## Key Differences From Java

| Concept | Java | Python |
|---|---|---|
| Quote style | Double quotes only | Single and double fully interchangeable |
| `==` behavior | Compares references — String Pool trap | **Always** compares content |
| Multi-line strings | Text blocks, Java 15+ only | Triple quotes, supported forever |
| `.length()` | Method | `len(string)` function |
| `.trim()` | — | `.strip()` |
| `.toUpperCase()` / `.toLowerCase()` | — | `.upper()` / `.lower()` |
| `.charAt(i)` | — | Direct indexing: `string[i]` |
| `.indexOf()` | — | `.find()` (returns -1) or `.index()` (crashes) |
| `.substring(a, b)` | — | Slicing: `string[a:b]` |
| `.contains()` | — | `in` keyword |
| `.equalsIgnoreCase()` | Built-in | **Doesn't exist** — `.lower()` both sides manually |
| `.isEmpty()` / `.isBlank()` | Built-in | **Don't exist** — compare to `""` or use truthiness |
| Reversing | `StringBuilder(...).reverse()` | `string[::-1]` |
| `String.join()` | Static method on String | Called on the separator: `" ".join(list)` |

## Key Rules / Gotchas Recap

- `==` on Python strings always compares content — the single biggest relief coming from Java
- `.join()` is called on the separator, not on the list — backwards from Java intuition, catches almost everyone at least once
- Strings remain immutable in Python exactly as in Java — every "modifying" method returns a new string

## Why This Structure Exists

Strings are foundational to nearly every program, and Python's design removes an entire category of Java's string pitfalls (the `==` trap) while introducing its own distinct vocabulary of method names and a genuinely more powerful slicing mechanism in place of individual methods like `substring()` and `charAt()`.