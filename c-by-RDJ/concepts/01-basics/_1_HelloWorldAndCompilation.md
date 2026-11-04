# `_1_HelloWorldAndCompilation.c`

## Concept
The smallest complete C program, and the four stages `gcc` runs to turn it into an executable. Unlike Java (compile to bytecode, run on a JVM), C compiles straight to native machine code your CPU executes.

## The Code

```c
#include <stdio.h>

int main(void) {
    printf("Hello, World!\n");
    printf("sizeof: char=%zu short=%zu int=%zu long=%zu pointer=%zu\n",
           sizeof(char), sizeof(short), sizeof(int), sizeof(long), sizeof(void *));
    return 0;
}
```

## Line-by-Line Breakdown

### `#include <stdio.h>`
Textual inclusion of the standard input/output header — it declares `printf` so the compiler can check your call. `<...>` searches system include paths; `"..."` searches your project first.

### `int main(void)`
The entry point. `int` because the program's exit status is returned to the shell; `void` means it takes no parameters — an empty `()` in C means unspecified parameters, so write `(void)`.

### `printf("Hello, World!\n");`
Prints to standard output. `\n` is the newline escape. The returned `int` (count of characters printed) is ignored here — later files check it.

### `sizeof`
A compile-time operator (not a function) giving a type's or value's size in bytes. Printed with `%zu` — the correct format for `size_t`, the type `sizeof` returns.

### `return 0;`
Exit status 0 = success. `echo $?` in the shell shows it. Reaching the end of `main` without a `return` also returns 0 in C99+.

## The Four Stages of `gcc`
1. **Preprocess** — expand `#include` and `#define` directives (`gcc -E`)
2. **Compile** — C to assembly for your CPU (`gcc -S`)
3. **Assemble** — assembly to machine code in an object file (`gcc -c`, gives `.o`)
4. **Link** — combine your object files with the standard library into one executable (`gcc` final step)

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _1_HelloWorldAndCompilation.c && ./demo
echo $?   # 0
```

## Why This Structure Exists
C's model: you write files, the compiler translates them exactly, and the linker stitches them together. No JVM, no runtime — which is why the same C skills underpin operating systems and the runtimes of Java and Python themselves.
