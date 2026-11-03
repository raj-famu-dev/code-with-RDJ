# `_1_FunctionAndClassTemplates.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A template is a recipe the compiler uses to generate real code for each type you use it with. `template <typename T> T maxOf(T a, T b)` is not a function yet; `maxOf(3, 7)` makes the compiler stamp out `int maxOf(int, int)`. Class templates such as `Stack<T>` work the same way and are how the entire standard library (`vector`, `map`, ...) is built.

Because the code is generated per type, templates are as fast as hand-written code for each type, and the compiler can check and optimize each instance. The price is longer compile times and long error messages.

## Full Line-by-Line Breakdown

### SECTION 1: a function template and deduction
`maxOf` takes two values of the same type `T`. The compiler deduces `T` from the arguments: `int` for `(3, 7)`, `double` for `(2.5, 1.5)`. You may also write `T` yourself: `maxOf<std::string>("pear", "apple")` converts the literals. `maxOf(1, 2.5)` does NOT compile because one argument says `int` and the other `double`; deduction does not guess. Spell it out with `maxOf<double>(1, 2.5)`. The function only needs `operator<` from `T` (it is written with `<` only, like a good generic algorithm).

Output from a real run:

```text
===== SECTION 1: a function template and deduction =====
maxOf(3, 7)         = 7   (T deduced as int)
maxOf(2.5, 1.5)     = 2.5 (T deduced as double)
maxOf<std::string>("pear", "apple") = pear (explicit T)
maxOf(1, 2.5) does NOT compile: one argument says int, the other double, so deduction fails.
Fix: maxOf<double>(1, 2.5) = 2.5 (explicit T converts the int)
```

### SECTION 2: a class template
`Stack<T>` stores a `std::vector<T>` and offers `push`, `pop`, `top`, `empty`, `size`. `Stack<int>` and `Stack<std::string>` are two unrelated classes generated from one definition. `pop` on an empty stack throws. The last lines show class template argument deduction (CTAD, C++17): `std::vector v{4, 5};` needs no `<int>`, and `std::pair p{1, 2.5};` becomes `pair<int,double>`.

Output from a real run:

```text
===== SECTION 2: a class template =====
Stack<int> top = 3, pop = 3, size now 2
Stack<std::string> pop = beta, then alpha
empty pop: pop on empty Stack
CTAD: `std::vector v{4, 5};` deduces std::vector<int>, size 2; `std::pair p{1, 2.5};` deduces pair<int,double>: 1,2.5
is_same<decltype(v), std::vector<int>>: true
```

### SECTION 3: instantiation: one generated copy per type
`instantiationCounter<T>()` holds a `static int`. Calling `touch<int>()` three times, `touch<double>()` once and `touch<std::string>()` twice gives three separate counters (3, 1, 2): proof that each `T` got its own function and its own static. The `sizeof` line shows both stacks are 24 bytes on this machine (the size of the vector handle: pointer triple), while the machine code for their member functions is different. This is the fundamental difference from Java, where there is exactly one compiled method for every `T`.

Output from a real run:

```text
===== SECTION 3: instantiation: one generated copy per type =====
calls recorded for int: 3, double: 1, std::string: 2
Each type got its own function with its own static variable. Java generics would have ONE method for all of them.
sizeof(Stack<int>) = 24, sizeof(Stack<std::string>) = 24 (both equal: each just holds one vector; the element code differs, not the handle)
```

### SECTION 4: specialization: the const char* pointer-compare trap
A generic `lessThan<const char*>` would compare two ADDRESSES, not the text, giving an arbitrary answer. An explicit specialization `template <> bool lessThan<const char*>(...)` replaces the generic code for that one type and uses `std::strcmp`. The output shows the text comparison is right ("banana" is not less than "apple"), and `lessThan(3, 4)` still uses the generic version. Specialize sparingly; overloads and concepts are usually better.

Output from a real run:

```text
===== SECTION 4: specialization: the const char* pointer-compare trap =====
Generic lessThan<const char*> would compare ADDRESSES (meaningless). Specialized version compares text.
lessThan(p1 = "banana", p2 = "apple") = false (strcmp: banana is not less than apple)
lessThan(p2, p1) = true
lessThan(3, 4) = true (generic version)
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Generics use TYPE ERASURE: `List<String>` and `List<Integer>` are the same class at run time; `T` becomes `Object` | Each `T` generates separate code (instantiation); there is no erasure |
| Type arguments must be reference types (`List<Integer>`, boxing) | Any type works, including `int`, with no boxing: `Stack<int>` stores raw ints |
| `new T()`, `T[]`, `instanceof T` are not allowed (erased) | `T x;`, `sizeof(T)`, `T::member` are all fine because T is known at compile time |
| Bounds: `<T extends Comparable<T>>` checked at the declaration | Requirements are implicit (it must compile for that T); C++20 adds concepts (next file) |
| Wildcards `? extends T` | No wildcards; each instantiation is a distinct type, with no subtype relation between `Stack<Base>` and `Stack<Derived>` |
| One method, one compiled body | Code size can grow with every type used (code bloat) |

Related Java points for this topic:
- Collections: `ArrayList<Integer>` boxes every int and shares one erased class; `std::vector<int>` is a distinct instantiation holding raw ints.
- Comparator: Java passes a `Comparator<T>` object; `maxOf` above simply requires `operator<` on `T`, checked when instantiated (a comparator can be passed as an extra template or function parameter).
- equals/hashCode: Java generic code calls `equals`/`hashCode` through `Object`; a C++ template calls `==` and `std::hash<T>` directly, resolved at compile time (file 7).

## Key Rules / Gotchas Recap
- Deduction needs consistent argument types; spell out `<T>` when they differ.
- The definition of a template usually lives in the header: the compiler needs it where it is instantiated.
- Errors appear at instantiation time, can be very long, and name the failing line inside the template.
- Pointers of `const char*` compare addresses unless you specialize or use `std::string`.
- Each instantiation has its own statics.

## Why This Structure Exists
Fast numeric and container code in AI engineering (tensor libraries, math kernels) depends on templates generating specialized, inlined code for each type with no runtime cost. Security tools use the same machinery for type-safe parsers and serializers.
