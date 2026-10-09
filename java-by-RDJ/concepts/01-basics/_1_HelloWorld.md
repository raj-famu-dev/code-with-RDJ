# `_1_HelloWorld.java`

## Concept
Program structure, the `main` method, and console output — the mandatory entry point every Java program needs.

## The Code

```java
public class _1_HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
```

## Line-by-Line Breakdown

### `public`
Access modifier meaning "visible to everyone, from any class." Used here because the JVM (Java Virtual Machine) needs to access this class from outside to start the program.

### `class`
Keyword that declares a blueprint/template. Everything in Java must live inside a class — there's no way to write "loose" code outside one.

### `_1_HelloWorld`
The name of the class. Must exactly match the filename (`_1_HelloWorld.java`), or the code won't compile.

### `{ }` (first pair)
Curly braces marking where the class body starts and ends — everything belonging to this class goes inside.

### `public static void main(String[] args)`
This exact line is required — it's the entry point the JVM looks for to start running your program.

| Part | Meaning |
|---|---|
| `public` | JVM must be able to call it from outside |
| `static` | Belongs to the class itself, not an object; runs without needing `new` to create anything first |
| `void` | Returns no value |
| `main` | The specific name Java expects to start execution |
| `(String[] args)` | Accepts an array of text arguments from the command line (unused here, but the signature is mandatory) |

### `{ }` (second pair)
Marks the start and end of the `main` method's body — the actual instructions run here.

### `System.out.println("Hello World");`

| Part | Meaning |
|---|---|
| `System` | A built-in Java class giving access to system-level tools |
| `out` | A field inside `System` representing the standard output stream (your console) |
| `println(...)` | A method that prints the given text and moves to a new line after |
| `"Hello World"` | The actual text (a `String`) being printed |
| `;` | Ends the statement — every instruction in Java needs one |

## Why This Structure Exists

Java enforces "everything lives in a class" and "one specific method starts the program" as strict rules, so the JVM always knows exactly where to begin, no matter how large or complex the codebase gets later.