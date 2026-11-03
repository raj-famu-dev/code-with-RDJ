# `_1_HelloWorldAndCompilation.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A C++ program is built from one or more translation units: a `.cpp` file after the preprocessor has pasted in every `#include`. Unlike Java, there is no virtual machine and no `.class` file: `g++` turns your source into native machine code in three steps (preprocess, compile, link) and gives you an executable that the operating system runs directly. Execution starts at the global function `main`, which returns an `int` exit code.

Knowing the three steps matters because the three kinds of error you will meet (a preprocessor/syntax error, a type error, and a linker error such as "undefined reference") each come from a different step.

## Full Line-by-Line Breakdown

### SECTION 1: HELLO WORLD
`#include <iostream>` makes the preprocessor paste the declarations of `std::cout` and friends into your file. `main` is the entry point; `std::cout << ...` sends text to standard output, and `\n` is the newline. `__cplusplus` is a macro the compiler defines with the language standard (`202002` means C++20), which is a quick way to prove which standard you are really compiling with.

Output from a real run:

```text
===== SECTION 1: HELLO WORLD =====
Hello, World!
Hello from C++ 202002 (YYYYMM of the language standard)
```

#### The three g++ steps, with numbers from a real run

```bash
g++ -std=c++20 -E _1_HelloWorldAndCompilation.cpp > hello.ii   # 1. preprocess
g++ -std=c++20 -S _1_HelloWorldAndCompilation.cpp -o hello.s   # 2a. compile to assembly
g++ -std=c++20 -c _1_HelloWorldAndCompilation.cpp -o hello.o   # 2b. assemble to an object file
g++ hello.o -o hello                                           # 3. link into an executable
```

1. **Preprocess (`-E`)**: handles every line that starts with `#`. The 47-line source grew to **43206 lines** after `#include <iostream>` and `<string>` were pasted in and macros expanded. You can see `SQUARE_BAD(n + 1)` become `n + 1 * n + 1` in that output.
2. **Compile (`-S`, `-c`)**: checks syntax and types and produces machine code. `-S` stops at human-readable assembly (**379 lines** here); `-c` produces an object file (`.o`, **6632 bytes** here). In the object file, `nm -C` shows `add(int, int)` and `main` as defined symbols (`T`) and `std::cout` as undefined (`U`): this file *uses* `cout` but does not contain it.
3. **Link**: the linker joins your object files with the C++ standard library and resolves every `U` symbol. The final executable here is **16912 bytes**, because the library is linked dynamically.

The two classic failures show the difference between compile and link errors. A missing semicolon (`int main() { return 0 }`) fails in the compile step:

```text
se.cpp:1:22: error: expected ';' before '}' token
```

Declaring a function and calling it without ever defining it compiles fine but fails at link time:

```text
undefined reference to `add(int, int)'
collect2: error: ld returned 1 exit status
```

### SECTION 2: WHAT THE PREPROCESSOR KNOWS
The preprocessor runs first and understands only text: `#include`, `#define`, `#ifdef`. `__LINE__` is replaced by the current line number (this number changes if you edit the file, which is expected), and `__GNUC__` tells you the compiler is GCC-compatible. `NDEBUG` is the macro that turns `assert` off in release builds; it is not defined in our `-O0` build.

Output from a real run:

```text
===== SECTION 2: WHAT THE PREPROCESSOR KNOWS =====
__LINE__ on this line is 25
Compiled by a GNU-compatible compiler, major version >= 13: true
NDEBUG is not defined (asserts would be active)
```

### SECTION 3: MACROS ARE JUST TEXT (TRAP)
`SQUARE_BAD(n + 1)` is replaced by the text `n + 1 * n + 1`, and because `*` binds tighter than `+` the result is `3 + 3 + 1 = 7`, not 16. `SQUARE_OK` wraps every use of the parameter in parentheses, which fixes this particular problem. The better fix in modern C++ is to avoid function-like macros and use a function or `constexpr` function, which evaluates its argument once and respects types.

Output from a real run:

```text
===== SECTION 3: MACROS ARE JUST TEXT (TRAP) =====
SQUARE_BAD(n + 1) = 7  (expected 16, got text substitution)
SQUARE_OK(n + 1)  = 16
A real function avoids this: add(n, 1) squared = 16
```

### SECTION 4: main AND THE EXIT CODE
`main` returns `int`, and `0` means success to the shell (`echo $?` shows it). `main` is the only function where leaving off `return` is allowed: the compiler adds `return 0;`. Any other non-void function that falls off the end is undefined behaviour. Command-line arguments arrive as `int main(int argc, char** argv)`, which later files in this curriculum use.

Output from a real run:

```text
===== SECTION 4: main AND THE EXIT CODE =====
main returns int; 0 means success to the shell.
If you omit 'return' in main only, the compiler inserts 'return 0;'.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `javac` makes bytecode, the JVM runs it | `g++` makes native machine code, the OS runs it |
| One public class per file, `public static void main(String[] args)` | A free function `int main()`, no class required |
| `import java.util.*;` loads a class from the classpath | `#include <vector>` literally pastes text into your file |
| Compile errors only; linking happens at class-load time | Separate link step: "undefined reference" errors appear after compiling succeeded |
| `System.out.println("x")` | `std::cout << "x" << '\n';` |
| No preprocessor | The preprocessor exists: `#define`, `#ifdef`, include guards |
| Same `.class` file runs everywhere | You compile per platform; the executable is tied to an OS and CPU |

## Key Rules / Gotchas Recap
- Three steps: preprocess (`g++ -E`), compile to assembly/object (`g++ -S` / `-c`), link (`g++ file.o -o prog`).
- Compile errors (type, syntax) and link errors (`undefined reference to ...`) are different problems with different fixes.
- Function-like macros are text substitution; always prefer `constexpr` functions or templates.
- `main` returns `int`; `0` is success. Only `main` gets the implicit `return 0`.
- Always compile with `-std=c++20 -Wall -Wextra -Wpedantic`; warnings are free bug reports.
- `#include` is text pasting, which is why large headers slow compilation.

## Why This Structure Exists
Understanding the toolchain is the first step to reading build failures, writing Makefiles/CMake, and later to security work such as reading compiler output, linking against libraries and understanding what actually ends up in a binary. AI engineering libraries (PyTorch, NumPy internals, inference runtimes) are native C++ code built exactly this way.
