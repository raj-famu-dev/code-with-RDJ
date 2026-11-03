# `_8_TemplateTraitsAndSFINAE.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Type traits (`<type_traits>`) are tiny compile-time functions that ask or transform facts about TYPES: "is this an integer?", "remove the reference from this type". Combined with `if constexpr`, SFINAE and `static_assert`, they let a template change its behavior or refuse to compile depending on the type it receives.

SFINAE ("Substitution Failure Is Not An Error") is the older technique: if forming a template's signature fails for some type, that overload is quietly dropped. C++20 concepts replace most of it, but you will meet SFINAE in existing code, so you need to read it.

## Full Line-by-Line Breakdown

### SECTION 1: type traits
`std::is_integral_v<T>`, `is_floating_point_v`, `is_pointer_v` and `is_const_v` are bool constants computed at compile time; `sizeof` is also shown (these byte sizes are for this x86-64 platform). Transformation traits produce a type: `std::remove_reference_t<int&>` is `int`; `std::decay_t<const int&>` is `int`. Conventions: `trait<T>::value` or `trait_v<T>` for a bool, `trait<T>::type` or `trait_t<T>` for a type.

Output from a real run:

```text
===== SECTION 1: type traits =====
  int: integral=true floating=false pointer=false const=false sizeof=4
  double: integral=false floating=true pointer=false const=false sizeof=8
  const char*: integral=false floating=false pointer=true const=false sizeof=8
  const long: integral=true floating=false pointer=false const=true sizeof=8
remove_reference_t<int&> is int: true, decay_t<const int&> is int: true
Traits are compile-time functions on TYPES: ::value (bool) or ::type / _t (a type).
```

### SECTION 2: if constexpr
`kind()` chooses a branch by type at compile time. The branches not taken are discarded and not even type-checked for that `T`, which is the key difference from a normal `if`. `describeSize` uses `requires { v.size(); }` to ask "does this expression compile?" With a plain `if`, `7.size()` would be a compile error for `int`; with `if constexpr`, that branch simply does not exist for `int`.

Output from a real run:

```text
===== SECTION 2: if constexpr =====
integer 42 | float 2.500000 | string "hi" | something else
describeSize(vector of 3) = 3, describeSize(7) = 1
A plain `if` here would not compile for int (7.size() is an error); `if constexpr` discards the branch at compile time.
```

### SECTION 3: SFINAE
`HasSize` is a "detection idiom": the default template is `false_type`. The specialization uses `std::void_t<decltype(std::declval<T>().size())>`, which only compiles if `.size()` exists, and then it is preferred and is `true_type`. For `int` the specialization fails to substitute, silently, and the default wins. The three `pretty` overloads each carry an `std::enable_if_t<condition, std::string>` return type: when the condition is false the whole signature is invalid and that overload disappears; exactly one remains for each argument. The output shows `int-like:5`, `sized:4` and `opaque`. If every overload is removed you get a long "no matching function" error: the pain that concepts were designed to fix. The same selection in C++20 would use `requires`.

Output from a real run:

```text
===== SECTION 3: SFINAE =====
HasSize<std::string>=true HasSize<int>=false HasSize<Blob>=false
int-like:5 | sized:4 | opaque
Each pretty() overload whose enable_if is false fails substitution and silently drops out; exactly one remains.
If NO overload remains you get 'no matching function' (a long error): the pain that concepts were created to fix.
```

### SECTION 4: compile-time checks
`Wrapper<T>` contains `static_assert(std::is_copy_constructible_v<T>, "...")`. Using it with a type that cannot be copied (such as `std::unique_ptr<int>`) would stop the compile with that message. The file cannot show that failing case and still compile, so it states it. Five more `static_assert`s sit at file scope; since the program runs, they all hold. Compile-time checks cost nothing at run time and fail early, where the bug is cheapest to fix.

Output from a real run:

```text
===== SECTION 4: compile-time checks =====
Wrapper<int> value = 9, Wrapper<std::string> value = copyable
Wrapper<std::unique_ptr<int>> would stop compilation with the message: "Wrapper<T> requires a copyable T".
5 static_assert lines at file scope were checked by the compiler; a false one would prevent this program from existing.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Generics erased: you cannot ask "is `T` an integer?" at run time from `T` alone, only through reflection/`instanceof` on values | `T` exists at compile time, so `std::is_integral_v<T>` is answered by the compiler with no run-time cost |
| `T extends Number` bounded type | Traits + `static_assert`, SFINAE, or (preferred) concepts |
| `instanceof`/overloading on the static type | `if constexpr` picks code per instantiated type |
| Cannot create `T[]` or `new T()` | `T` is a real type: `sizeof(T)`, `T{}` are fine |
| Reflection inspects members at run time (slow, unsafe) | Detection idioms inspect members at compile time |
| Compile error names the generic bound | Error may be long; `static_assert` messages let you write your own |

Related Java points for this topic:
- Collections: generic collection code in Java cannot branch on `T` because of type erasure; C++ library containers use traits to pick, for example, a `memmove` fast path for trivially copyable element types.
- Comparator, equals and hashCode: C++ standard code asks traits such as `std::is_nothrow_move_constructible_v<T>` or `std::is_invocable_v<Cmp, T, T>` (does this comparator work on `T`?) and `std::is_default_constructible_v<std::hash<T>>` (is T hashable?); Java answers these only with interfaces (`Comparable`, `Object.hashCode`) at run time.

## Key Rules / Gotchas Recap
- Use `_v` and `_t` helper variants (`is_integral_v`, `remove_reference_t`).
- `if constexpr` discards untaken branches only inside a template; outside a template both branches must compile.
- A substitution failure must happen in the signature (return type, parameter, template parameter) to count as SFINAE; failure inside the body is a hard error.
- Prefer concepts in C++20 code; read SFINAE in older code.
- `static_assert` with a message is the cheapest way to document a template's requirements.

## Why This Structure Exists
High-performance libraries choose algorithms by type at compile time (for example, a memcpy fast path for trivially copyable types) with no run-time branching. The same tools let security and serialization code refuse unsafe types, such as copying a non-trivial type with `memcpy`, before the program ever runs.
