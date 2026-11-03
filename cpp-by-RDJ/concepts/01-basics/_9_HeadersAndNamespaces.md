# `_9_HeadersAndNamespaces.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A declaration tells the compiler a name exists and what its type is; a definition actually creates the function or variable. C++ lets you declare something many times but requires exactly one definition (the One Definition Rule, ODR), which is why large programs split declarations into `.h` header files and definitions into `.cpp` files. Namespaces group names so that two libraries can both have a function called `name` without clashing.

This file keeps everything in one translation unit and marks regions as "pretend this is shapes.h / shapes.cpp / main.cpp". The real multi-file build is explained below.

## Full Line-by-Line Breakdown

### SECTION 1: DECLARATION VS DEFINITION
`double area_of_circle(double r);` is a declaration (the signature only). Its definition, with a body, appears once in the "cpp" region. An `inline` function and a `constexpr` variable are allowed to be defined in a header because they are exempt from the one-definition restriction (every file gets an identical copy). A class definition can also appear in many files as long as every definition is identical; methods defined inside the class are implicitly inline.

Output from a real run:

```text
===== SECTION 1: DECLARATION VS DEFINITION =====
area_of_circle(2) = 12.5664 (declared in 'header', defined once in 'cpp')
twice(21) = 42 (inline: definition may repeat in every file)
A declaration says 'this exists'; a definition creates it. Many declarations are OK, exactly one definition.
```

### SECTION 2: INCLUDE GUARDS AND ODR
The region between `#ifndef SHAPES_H` and `#endif` is an include guard. The first time, `SHAPES_H` is undefined, so the contents are processed and the macro is defined. A SECOND simulated inclusion (which tries to redefine `class Counter`) is skipped because the macro now exists; without the guard the compiler would report a redefinition. (`#pragma once` does the same job and is widely supported, but the guard is standard C++.) The program prints that the macro is defined. The ODR trap is described in the code: a non-inline function defined in a header and included from two `.cpp` files compiles fine everywhere but fails at link time with "multiple definition".

Output from a real run:

```text
===== SECTION 2: INCLUDE GUARDS AND ODR =====
Counter value = 2
Guard macro SHAPES_H defined: yes
```

### SECTION 3: NAMESPACES
`mylib::name()` and `otherlib::name()` coexist. A `using` declaration inside a block imports one name for that block only, a namespace alias (`namespace ml = mylib;`) shortens long names, and an anonymous namespace gives a helper internal linkage so other `.cpp` files cannot see it. A nested `detail` namespace is the conventional "internal, do not use" marker. Never write `using namespace std;` in a header: every file that includes it silently inherits all of `std`.

Output from a real run:

```text
===== SECTION 3: NAMESPACES =====
mylib::name vs otherlib::name
mylib::detail::secret
using-declaration: mylib::name
alias: mylib::name
anonymous namespace helper = 42
```

#### How the real multi-file build works

A real project would contain three files:

```text
shapes.h     declarations only, with an include guard
shapes.cpp   the definitions; it does #include "shapes.h"
main.cpp     uses shapes::area_of_circle; it does #include "shapes.h"
```

`shapes.h`:

```cpp
#ifndef SHAPES_H
#define SHAPES_H
namespace shapes {
double area_of_circle(double r);
}
#endif
```

`shapes.cpp` includes the header (so the compiler checks the definition matches the declaration) and defines the function; `main.cpp` includes the header and calls it. Each `.cpp` is a separate translation unit compiled on its own to an object file, and the linker then connects the call in `main.o` to the definition in `shapes.o`. Verified with `nm -C`: `main.o` lists `shapes::area_of_circle(double)` as `U` (undefined, needs linking) and `shapes.o` lists it as `T` (defined).

A minimal Makefile (tested; `make` builds `app`, which prints `12.5664`):

```make
CXX := g++
CXXFLAGS := -std=c++20 -Wall -Wextra -Wpedantic -O0
OBJS := main.o shapes.o

app: $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJS)

%.o: %.cpp shapes.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f app *.o

.PHONY: clean
```

Reading it: `app` depends on the object files, and the pattern rule `%.o: %.cpp shapes.h` rebuilds an object when its `.cpp` or the header changes. Recipe lines must start with a TAB, not spaces. `make` rebuilds only what changed, which is the whole point: with hundreds of files you do not recompile everything. CMake generates files like this for larger projects.

## Key Differences From Java
| Java | C++ |
|---|---|
| `package com.x;` plus folder layout | `namespace x { }` can be declared anywhere; folders are not tied to it |
| One class per file, compiler finds it | Header (`.h`) declares, source (`.cpp`) defines; you list files to build |
| `import` | `#include` (text paste) and `using` (names) are separate ideas |
| `private`/`package-private` hides from other packages | Anonymous namespace / `static` give internal linkage; headers are not enforced access control |
| No duplicate-definition problem | One Definition Rule: duplicates cause link errors; include guards prevent redefinition errors |
| `javac *.java` or Maven | Compile each `.cpp` to `.o`, then link; use Make or CMake |

## Key Rules / Gotchas Recap
- Declaration = what it is; definition = the thing itself. Many declarations, ONE definition.
- Every header needs an include guard (or `#pragma once`).
- Put definitions in `.cpp` files; in headers only `inline`/`constexpr`/templates/class bodies.
- Do not write `using namespace std;` in a header.
- Anonymous namespaces make helpers private to the file.
- `undefined reference` means a missing definition (or a missing `.o`/library on the link line); `multiple definition` means too many.

## Why This Structure Exists
Real C++ projects (inference engines, security tools, game engines) are hundreds of translation units, and build errors come from exactly these rules. Understanding declarations, definitions and linkage also underlies how libraries are linked, which matters when reading or auditing native code.
