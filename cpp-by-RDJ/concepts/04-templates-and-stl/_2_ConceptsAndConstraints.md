# `_2_ConceptsAndConstraints.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A C++20 concept is a named, compile-time-checked requirement on a template parameter, such as "T must be a number" or "T must support `+`". You write the requirement once and use it to constrain templates, which documents intent and produces error messages that name the unmet requirement at the call site.

Before concepts, constraints were done indirectly with SFINAE tricks (file 8). Concepts replace most of that with readable code.

## Full Line-by-Line Breakdown

### SECTION 1: defining concepts
`Numeric` is just a boolean compile-time expression: `std::is_arithmetic_v<T>`. `Addable` uses a `requires` expression: "given `a` and `b` of type `T`, `a + b` must be valid and its result must convert to `T`". `Printable` requires `os << v` to compile. `NoPlus` has none of the operations; `Meter` has `+` but no `<<`. The program prints each concept's value as a plain bool.

Output from a real run:

```text
===== SECTION 1: defining concepts =====
Numeric<int>=true Numeric<double>=true Numeric<std::string>=false
Addable<int>=true Addable<std::string>=true Addable<Meter>=true Addable<NoPlus>=false
Printable<int>=true Printable<Meter>=false (Meter has no operator<<)
```

### SECTION 2: three ways to constrain
1. `template <Numeric T> T twice(T x)` constrains the parameter directly.
2. `requires Addable<T> && Printable<T>` is a requires-clause; you combine concepts with `&&` and `||`.
3. `std::floating_point auto` in a function signature constrains an abbreviated template parameter.

Calling `twice` with a string is rejected at the call, before the body is examined. The real compiler message (copied from an actual failing compile of that call, trimmed) was:

```text
error: no matching function for call to 'twice(std::string)'
note: candidate: 'template<class T>  requires  Numeric<T> T twice(T)'
note: constraints not satisfied
note: the expression 'is_arithmetic_v<T> [with T = std::string]' evaluated to 'false'
```

You get the function, the named constraint and the exact failing check. For comparison, calling an UNCONSTRAINED `twice(T x){return x + x;}` with a struct that has no `+` gives `error: no match for 'operator+' (operand types are 'NoPlus' and 'NoPlus')` pointing INSIDE the function body ("In instantiation of ... required from here"). That is a fair message for a one-line function; the difference grows when the failing use is several layers deep inside library code, because a concept reports the problem at the boundary instead of deep in the implementation.

Output from a real run:

```text
===== SECTION 2: three ways to constrain =====
twice(21) = 42, twice(1.5) = 3
twice(std::string("x")) would fail the Numeric constraint at the call site, before the body is looked at.
  sum = 5
  sum = concat
showSum(Meter{1}, Meter{2}) would not compile: Meter is Addable but not Printable.
average({1.0, 2.0, 6.0}) = 3
```

### SECTION 3: overloading on concepts
Three `describe` overloads: unconstrained, `std::integral`, `std::floating_point`. The call picks the most constrained one that fits: `5` gets the integral version, `2.5` the floating-point version, and a `std::string` falls back to the generic one. No tag dispatch or `enable_if` is needed.

Output from a real run:

```text
===== SECTION 3: overloading on concepts =====
describe(5)      -> an integer type
describe(2.5)    -> a floating-point type
describe("hi"s)  -> something generic
The most constrained viable overload wins; no tag dispatch or SFINAE tricks needed.
```

### SECTION 4: compile-time checks
`static_assert(Concept<T>)` verifies facts at compile time. Five of them sit at namespace scope; if any were false the file would not compile, so the program running at all proves they hold. The last line just shows `Meter`'s `+` working.

Output from a real run:

```text
===== SECTION 4: compile-time checks =====
This file contains 5 static_assert lines at namespace scope.
They were verified by the compiler: if any were false, the file would not compile.
Meter{1.5} + Meter{2.0} = 3.5
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Bounded generics: `<T extends Number & Comparable<T>>` | Concepts: `template <typename T> requires Numeric<T> && std::totally_ordered<T>` |
| Bounds are about inheritance (a type must extend/implement) | Concepts are about SYNTAX/BEHAVIOR (a type just needs to support the operations); no inheritance required, so `int` works |
| Type erasure: `T` becomes its bound (`Object`/`Number`) at run time; you cannot call `T`-specific static things or `new T()` | No erasure: `T` is a real type, so a concept can check `sizeof`, nested types, operators, anything |
| Cannot constrain `int` (primitives are not allowed as `T`; use `Integer`) | Built-in types satisfy concepts directly (`Numeric<int>`) |
| Error: "incompatible types: inference variable T has incompatible bounds" | Error: names the concept and the failing expression |
| Constraint failure is checked against the declared bound only | A constrained template is checked at the call; inside the body, only the declared operations are guaranteed by convention (not enforced) |

Related Java points for this topic:
- Collections: `Collections.max(Collection<? extends T>)` requires `T extends Comparable<? super T>`; the C++ equivalent constraint is `std::totally_ordered<T>` (or `std::ranges::max` with a comparator).
- Comparator: Java expresses ordering as an interface (`Comparable`/`Comparator`); a C++ concept such as `std::totally_ordered` only checks that `<`, `==` and friends compile, so built-in `int` qualifies with no wrapper.
- equals/hashCode: the standard concept `std::equality_comparable<T>` checks `==`; hashing has its own requirement (a `std::hash<T>` that works), in place of Java's every-Object `hashCode`.

## Key Rules / Gotchas Recap
- A concept is a compile-time boolean on types; combine with `&&`, `||`, `!`.
- `requires(T a, T b) { a + b; }` checks that the expression is valid, not that it runs.
- The most constrained overload wins; concepts are ranked by subsumption.
- Prefer standard concepts from `<concepts>` (`std::integral`, `std::copyable`, `std::totally_ordered`...) before writing your own.
- Concepts check syntax, not meaning: `Addable<std::string>` is true although "adding" strings is concatenation.

## Why This Structure Exists
Libraries for tensors, containers and parsers expose generic functions to many users. Concepts turn "it fails somewhere deep inside the template" into "your type does not satisfy X", which makes generic code usable by engineers who did not write it.
