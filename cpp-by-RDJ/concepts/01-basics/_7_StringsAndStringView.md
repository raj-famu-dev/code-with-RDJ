# `_7_StringsAndStringView.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`std::string` is a mutable, value-semantics string that owns its characters: copying it copies the text, and `==` compares content. `std::string_view` is a lightweight non-owning window (pointer plus length) over characters owned by someone else, which makes it ideal for read-only function parameters but dangerous if the owner dies first. Short strings are stored inside the string object itself (small string optimisation), so tiny strings need no heap allocation.

## Full Line-by-Line Breakdown

### SECTION 1: std::string BASICS
Strings are built with `+=` and `push_back`, are mutable (`s[0] = 'J'` works; Java's `String` is immutable), and `substr(pos, len)` and `find` work as expected; `find` returns `std::string::npos` when nothing matches. A copy is independent of the original. `==` compares text, so unlike Java there is no `equals()` pitfall, and `<` compares lexicographically.

Output from a real run:

```text
===== SECTION 1: std::string BASICS =====
Hello, World! (size 13)
after s[0] = 'J': Jello, World!
substr(7, 5) = World, find("World") = 7
find("zzz") == npos: true
copy: Hello, World! | original: Jello, World! (independent)
== compares CONTENT: true (Java needs equals())
"apple" < "banana": true
```

### SECTION 2: SMALL STRING OPTIMISATION (SSO)
The printed numbers are measurements of this library (libstdc++ with g++ 13) and not language guarantees. A string like `"hi"` reports capacity 15: it lives in a 16-byte buffer inside the 32-byte string object, with no heap allocation. A 100-character string must use the heap. `sizeof(std::string)` is the same for both because the object always has the same fields; only where the characters live changes.

Output from a real run:

```text
===== SECTION 2: SMALL STRING OPTIMISATION (SSO) =====
capacity of "hi" = 15 (measurement: inline buffer in libstdc++)
capacity of a 100-char string = 100 (heap allocated)
sizeof(std::string) = 32 (measurement, same for short and long strings)
```

### SECTION 3: std::string_view
A `string_view` holds just a pointer and a length (16 bytes here), copies nothing, and accepts a `std::string`, a literal or a sub-range. `count_char` takes a `string_view` so one function serves all of them without allocation. Because the view points at the owner's bytes, changing `owner[0]` changes what the view reads (`banana` becomes `Banana`): a view is a window, not a copy.

Output from a real run:

```text
===== SECTION 3: std::string_view =====
word = banana, count of 'a' = 3
count_char with a literal: 4
after owner[0]='B', the view reads: Banana (it is a window, not a copy)
sizeof(string_view) = 16 (pointer + length; measurement)
```

### SECTION 4: THE DANGLING string_view TRAP
The view `dangling` points into `inner`, which is destroyed at the closing brace. Afterwards the view still holds the old pointer and length, but reading through it would be undefined behaviour, so the demo only prints the stored size and then resets the view. The commented `bad()` shows another common form: returning a `string_view` into a local string. The fix is to return an owning `std::string`, or make sure the owner outlives every view. Also remember a view is not null-terminated, so passing `v.data()` to a C function can read past the end.

Output from a real run:

```text
===== SECTION 4: THE DANGLING string_view TRAP =====
inside scope the view is fine, size 67
after scope the view is dangling (size 67 is still stored, but reading it would be undefined behaviour; we do not read it)
good() returns an owning string: temporary
string_view is not null-terminated; never pass v.data() to a C function expecting a C string.
```

### SECTION 5: COMPARISON WITH JAVA String
A summary of the semantic differences, printed so it can be compared with the Java notes in the walkthrough below.

Output from a real run:

```text
===== SECTION 5: COMPARISON WITH JAVA String =====
Java: immutable, GC-managed, interned literals, == compares references.
C++ std::string: mutable value type, deep copy on assignment, == compares content.
Java substring() gives you a new safe String; string_view is a raw borrow that you must keep alive yourself.
```

## Key Differences From Java
| Java `String` | C++ `std::string` / `std::string_view` |
|---|---|
| Immutable | `std::string` is mutable |
| Reference type, garbage collected | Value type that owns its buffer; destroyed at scope end |
| `a == b` compares references; `equals()` compares text | `a == b` compares text |
| `substring()` returns a new String (safe) | `substr()` copies; `string_view::substr()` does not copy but borrows |
| String pool / interning of literals | Literals are `const char[]`; they become `std::string` only when you convert |
| UTF-16 internally, `char` is 16 bits | Bytes (`char` is 8 bits); UTF-8 text is just bytes, and `size()` counts bytes, not characters |
| No dangling possible | `string_view` can dangle if its owner dies |

## Key Rules / Gotchas Recap
- `std::string` is a mutable value; assignment copies the characters.
- `==` compares content; `find` returns `npos` when absent.
- SSO: short strings need no heap allocation (library-specific detail).
- `string_view` borrows: never let it outlive the string it views, and never return a view of a local.
- `string_view` is not null-terminated.
- `std::string s = "a" + "b";` does not compile: two literals cannot be added.

## Why This Structure Exists
Text handling is everywhere in AI and security work (tokenisers, log parsers, protocol parsers), and `string_view` is the tool that lets those code paths avoid millions of copies. It is also exactly the kind of non-owning borrow where lifetime mistakes become use-after-free vulnerabilities, so understanding it early pays off.
