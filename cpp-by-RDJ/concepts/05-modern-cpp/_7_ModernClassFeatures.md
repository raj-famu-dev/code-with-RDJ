# `_7_ModernClassFeatures.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Modern C++ gives you small, explicit tools for writing classes: `= default` asks the compiler to generate a special member, `= delete` forbids an operation, a defaulted `operator<=>` generates all six comparison operators, designated initializers name the fields you set, `enum class` gives scoped, type-safe enums, `using` makes readable aliases (including templates), and attributes such as `[[nodiscard]]` and `[[deprecated]]` add compiler-checked intent. Each one removes a class of boilerplate or a class of bug.

## Full Line-by-Line Breakdown

### SECTION 1: = default AND = delete
`Account` says exactly what it can do. `Account() = default` asks for the compiler-generated default constructor. `= delete` on the copy constructor and copy assignment makes copying a compile error (`Account d = c;` fails with "use of deleted function"; verified by compiling it). The move operations are defaulted, so `Account c = std::move(b)` works and the owner name `raj` travels to `c`. `take_int(double) = delete` shows delete is not only for special members: `take_int(2.5)` fails to compile instead of silently converting to `int`.

Output from a real run:

```text
===== SECTION 1: = default AND = delete =====
default-constructed owner: nobody, named owner: raj
moved account owner: raj
Account copy = delete: 'Account d = c;' is a COMPILE ERROR (try it).
take_int(5)
take_int(2.5) is a COMPILE ERROR because the double overload is deleted.
```

### SECTION 2: DEFAULTED COMPARISONS
`auto operator<=>(const Version&) const = default;` generates `<`, `<=`, `>`, `>=` (and, with `==` defaulted too, `==` and `!=`) by comparing members in declaration order. `1.2.3 < 1.10.0` is true because minor 2 < 10. `std::set<Version>` works because the type is now ordered, and the two equal versions collapse to one. TRAP: the field order IS the comparison order; moving `patch` above `major` would change every result.

Output from a real run:

```text
===== SECTION 2: DEFAULTED COMPARISONS =====
v1 == v3: true
v1 < v2:  true  (minor 2 < 10; member order decides)
v2 >= v1: true
(v1 <=> v2) < 0: true
std::set<Version> size (v1 and v3 equal): 2, smallest is 1.2.3
TRAP: the order of the data members IS the comparison order. Reordering fields changes behaviour.
```

### SECTION 3: DESIGNATED INITIALIZERS
C++20 designated initializers let you write `Config{.host = "example.test", .port = 8080}`. Skipped fields take their default member initializer (`verbose=false`). TRAP: designators must follow declaration order; `{.port = 1, .host = "x"}` is a compile error in C++ ("designator order ... does not match declaration order"; verified by compiling it), unlike C99.

Output from a real run:

```text
===== SECTION 3: DESIGNATED INITIALIZERS =====
c1: example.test:8080 verbose=false
c2: localhost:80 verbose=true (unnamed fields use defaults)
TRAP: designators must appear in declaration order; {.port = 1, .host = "x"} does not compile in C++.
```

### SECTION 4: enum class
`enum class Color` is scoped (`Color::Red`) and does not convert to int implicitly; `static_cast<int>(col)` is required. You can choose the underlying type (`Level : unsigned char` has size 1). The classic `enum OldColor` converts silently to `int` and leaks `OLD_RED` into the enclosing scope. Verified compile errors: `int x = Color::Red;` fails ("cannot convert 'Color' to 'int'").

Output from a real run:

```text
===== SECTION 4: enum class =====
name(Color::Green) = Green
underlying value: 1 (conversion must be explicit)
Level::High underlying: 10, sizeof(Level)=1
classic enum OLD_GREEN converts silently to int: 1
TRAP: 'int x = Color::Red;' and 'Color::Red == 0' do not compile; that is the point.
```

### SECTION 5: using ALIASES
`using ScoreTable = std::map<std::string, std::vector<int>>;` gives a long type a short name, and `template <class T> using Grid = std::vector<std::vector<T>>;` is a template alias, something old `typedef` cannot do. The output shows a table with 2 entries and a 2x3 grid filled with 7.

Output from a real run:

```text
===== SECTION 5: using ALIASES =====
ScoreTable entries: 2, ana's scores: 2
Grid<int> is 2x3, grid[1][2]=7
'using' replaces typedef and, unlike typedef, supports templates.
```

### SECTION 6: ATTRIBUTES
`[[nodiscard]]` makes the compiler warn when a caller ignores a return value (verified: a bare `checked_divide(1, 0);` gives a `-Wunused-result` warning). `[[deprecated("...")]]` warns whenever the function is called (verified: `-Wdeprecated-declarations` with the message). `[[maybe_unused]]` silences unused-variable warnings where intentional, and `[[fallthrough]]` marks an intentional switch fall-through so `-Wextra` does not complain; the output shows case 2 falling into case 3.

Output from a real run:

```text
===== SECTION 6: ATTRIBUTES =====
checked_divide(10, 2) = 5
TRAP: a bare 'checked_divide(1, 0);' triggers a [[nodiscard]] warning; deprecated old_divide warns when called.
level two, falling through on purpose
level three code also ran
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `record Version(int major, int minor, int patch)` gives `equals`, `hashCode`, `toString` automatically. | Defaulted `operator<=>` and `operator==` give comparisons; there is no auto `toString`. |
| Make a class non-copyable by not exposing copy logic (no copy ctor exists by default for references). | `= delete` explicitly removes copy; `= default` re-enables compiler versions. |
| `enum Color { RED }` is already scoped and type-safe; can have fields and methods. | `enum class` is scoped and type-safe but only an integer type with names; no methods. |
| Builders or constructor chains for optional parameters. | Designated initializers (in declaration order), default member initializers. |
| `@Override`, `@Deprecated`, `@FunctionalInterface` annotations. | `[[nodiscard]]`, `[[deprecated]]`, `[[maybe_unused]]`, `[[fallthrough]]` attributes (compiler hints, not reflection data). |
| Type aliases do not exist (use a subclass or wrapper). | `using` aliases, including template aliases. |

## Key Rules / Gotchas Recap
- `= default` generates the member; `= delete` makes using it a compile error (works on any function).
- Defaulted `<=>` compares members in declaration order; also default `==` explicitly when mixing.
- Designated initializers: names must be in declaration order and you cannot mix named and positional.
- Prefer `enum class` over plain `enum`; cast to the integer type explicitly.
- Prefer `using` over `typedef`.
- `[[nodiscard]]` on functions whose result must not be ignored (error codes, results).
- Attributes are hints; do not rely on them for program logic.

## Why This Structure Exists
These features make classes safer by construction: types that cannot be accidentally copied (resources, locks, sockets), enums that cannot be mixed up, and results that cannot be ignored. That is the same discipline that prevents real bugs in infrastructure and security code.
