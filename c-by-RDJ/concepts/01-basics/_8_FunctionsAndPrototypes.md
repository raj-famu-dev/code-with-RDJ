# `_8_FunctionsAndPrototypes.c`

## Concept
Functions, prototypes, and the rule that changes how you think coming from Java: **C only has pass-by-value**. There is no pass-by-reference — you pass an address *by value*, and the function follows it.

## The Code

```c
#include <stdio.h>

int add(int a, int b);
void swap_fail(int a, int b);
void swap_works(int *a, int *b);

int main(void) {
    printf("add(2, 3) = %d\n", add(2, 3));

    int x = 1, y = 2;
    swap_fail(x, y);
    printf("after swap_fail:  x=%d y=%d\n", x, y);

    swap_works(&x, &y);
    printf("after swap_works: x=%d y=%d\n", x, y);
    return 0;
}

int add(int a, int b) {
    return a + b;
}

void swap_fail(int a, int b) {
    int tmp = a; a = b; b = tmp;
}

void swap_works(int *a, int *b) {
    int tmp = *a; *a = *b; *b = tmp;
}
```

## Line-by-Line Breakdown

### `int add(int a, int b);` — the prototype
Declares the signature only: name, return type, parameter types. It lets the compiler type-check calls made *before* the definition appears. All three prototypes at the top are the "header" pattern in miniature — in real projects they'd live in a `.h` file.

### `void`
"Returns nothing." A `void` function's body ends with an implicit return; `return;` exits early.

### `swap_fail` — the copies
Arguments are **copied** into the parameters. Swapping `a` and `b` swaps copies; the caller's `x` and `y` never move. Java does the same thing — but Java object variables *are* references, so copying the reference still reaches the object. C has no references; that's the whole difference.

### `swap_works` — addresses by value
`&x` passes the *address* (still by value — the address is copied). Inside, `*a` follows the address to the caller's actual storage. This is "pass-by-reference" emulated on pass-by-value, and it is the idiom for every out-parameter in C.

### `return a + b;`
Exit point and value in one statement. A function that falls off the end while its caller uses the value is undefined behavior.

## Traps
- Calling an undeclared function is a compile error in C99+ — always prototype (or define before use).
- `void f()` in C means *unspecified* parameters; write `void f(void)` for "no parameters".
- Forgetting to use a function's return value (e.g. `snprintf`) loses error information — GCC warns with `-Wunused-result` on some.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _8_FunctionsAndPrototypes.c && ./demo
```

## Why This Structure Exists
Prototypes exist because the compiler works top-to-bottom, and multi-file builds need one place to state the contract (the header). And pass-by-value-only exists because it's one uniform, cheap rule — addresses give you the rest.
