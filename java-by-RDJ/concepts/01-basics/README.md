# 📘 01 — Java Basics

> Foundational Java syntax and core language mechanics — the building blocks every later concept (OOP, collections, exceptions, multithreading) depends on.

![Language](https://img.shields.io/badge/Language-Java%2021-orange)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Type](https://img.shields.io/badge/Type-Concept%20Practice-blue)

---

## 📌 About This Folder

Each file here is a **standalone, runnable program** isolating exactly one core Java concept. This isn't just a code dump — every program is documented below with the concept it teaches, why that concept matters, its syntax pattern, and the gotchas that trip people up.

Every concept also has its own dedicated `.md` explanation file — a full line-by-line breakdown of that specific program, going deeper than the summary in this README.

This README serves two purposes:
1. **My own reference** — a fast lookup for syntax I've already learned.
2. **A portfolio artifact** — proof of what I understand and can build with, for anyone reviewing this repo.

---

## ✅ Progress Tracker

| # | File | Concept | Explanation | Status |
|---|------|---------|:---:|:---:|
| 1 | [`_1_HelloWorld.java`](./_1_HelloWorld.java) | Program structure & output | [📄 Explained](./_1_HelloWorld.md) | ✅ |
| 2 | [`_2_VariablesAndDataTypes.java`](./_2_VariablesAndDataTypes.java) | Variables & primitive types | [📄 Explained](./_2_VariablesAndDataTypes.md) | ✅ |
| 3 | [`_3_Operators.java`](./_3_Operators.java) | Arithmetic, relational, logical ops | [📄 Explained](./_3_Operators.md) | ✅ |
| 4 | [`_4_TypeCasting.java`](./_4_TypeCasting.java) | Implicit vs explicit casting | [📄 Explained](./_4_TypeCasting.md) | ✅ |
| 5 | [`_5_ControlFlow.java`](./_5_ControlFlow.java) | if/else, switch | [📄 Explained](./_5_ControlFlow.md) | ✅ |
| 6 | [`_6_Loops.java`](./_6_Loops.java) | for, while, do-while | [📄 Explained](./_6_Loops.md) | ✅ |
| 7 | [`_7_Arrays.java`](./_7_Arrays.java) | 1D & 2D arrays | [📄 Explained](./_7_Arrays.md) | ✅ |
| 8 | [`_8_Strings.java`](./_8_Strings.java) | String methods & immutability | [📄 Explained](./_8_Strings.md) | ✅ |
| 9 | [`_9_Methods.java`](./_9_Methods.java) | Parameters, return types, overloading | [📄 Explained](./_9_Methods.md) | ✅ |
| 10 | [`_10_UserInput.java`](./_10_UserInput.java) | Scanner & console input | [📄 Explained](./_10_UserInput.md) | ✅ |
| 11 | [`_11_OutputFormating.java`](./_11_OutputFormating.java) | printf, String.format, text blocks | [📄 Explained](./_11_OutputFormating.md) | ✅ |

**`01-basics` is complete — all 11 topics, each with full code and a matching line-by-line explanation file.**

> 📎 Note: an `ExceptionHandling` practice file was also written during this phase but has been moved to `concepts/04-exceptions/` since that's where it topically belongs — it'll be logged in that folder's own README.

---

## 🗂 Concept Log

### 1️⃣ `_1_HelloWorld.java`
**Concept:** Program structure, the `main` method, console output

**Why it matters:** Every Java program needs a class containing a `main` method — this is the JVM's required entry point. Nothing runs without it.

**Syntax formula:**
```java
public class ClassName {
    public static void main(String[] args) {
        System.out.println("text");
    }
}
```

**Key rules:**
- File name must match the public class name exactly (`ClassName.java`)
- `main` must be `public static void main(String[] args)` — the JVM looks for this exact signature

**Implementation notes:**
> Prints `"Hello, RDJ is coding!"` to console. First working Java program in this repo — confirmed JDK 21 and IntelliJ project setup were correctly configured after resolving a package-statement error caused by hyphenated folder names (`01-basics` isn't a valid Java package name, so Sources Root marking had to be removed).

---

### 2️⃣ `_2_VariablesAndDataTypes.java`
**Concept:** Declaring variables, Java's 8 primitive data types

**Why it matters:** Java is statically typed — every variable's type is fixed at declaration and checked at compile time. This is what lets the compiler catch type errors before the program ever runs, instead of failing unpredictably at runtime.

**Syntax formula:**
```java
dataType variableName = value;
```

| Type | Size | Example |
|---|---|---|
| `byte` | 8-bit | `byte b = 127;` |
| `short` | 16-bit | `short s = 30000;` |
| `int` | 32-bit | `int i = 42;` |
| `long` | 64-bit | `long l = 42L;` |
| `float` | 32-bit decimal | `float f = 3.14f;` |
| `double` | 64-bit decimal | `double d = 3.14159;` |
| `char` | 16-bit Unicode | `char c = 'A';` |
| `boolean` | true/false | `boolean flag = true;` |

**Key rules / gotchas:**
- `float` and `long` literals need the `f` / `L` suffix, or the compiler assumes `double`/`int` and may error
- Primitives have **default values** when used as class fields (`0`, `0.0`, `false`, `'\u0000'`) — but **local variables have no default** and must be initialized before use

**Implementation notes:**
> Covered all 8 primitives, `String` basics, implicit/explicit casting intro, `final` constants, and `var` type inference in one file. Also tested naming conventions (camelCase vs PascalCase vs ALL_CAPS for constants).

---

### 3️⃣ `_3_Operators.java`
**Concept:** Arithmetic, relational, logical, and assignment operators

**Why it matters:** Operators are how programs make decisions and compute values — they're the mechanical layer beneath every `if` statement and loop condition you'll write from here on.

**Syntax formula:**
```java
// Arithmetic:   +  -  *  /  %
// Relational:   ==  !=  >  <  >=  <=
// Logical:      &&  ||  !
// Assignment:   =  +=  -=  *=  /=
```

**Key rules / gotchas:**
- `/` between two `int`s does **integer division** (`7 / 2` → `3`, not `3.5`) — cast one operand to `double` to get a decimal result
- `%` gives the remainder, useful for even/odd checks (`n % 2 == 0`)
- `&&` and `||` **short-circuit** — the second operand isn't evaluated if the first already determines the result

**Implementation notes:**
> Also covered unary operators (pre vs post increment/decrement — the classic `y++` vs `++z` distinction), bitwise operators (`& | ^ ~ << >>`), the ternary operator, and full operator precedence order.

---

### 4️⃣ `_4_TypeCasting.java`
**Concept:** Implicit (widening) vs explicit (narrowing) type conversion

**Why it matters:** Java won't silently convert between incompatible types unless you tell it to — this prevents accidental data loss, but means you need to understand which conversions need an explicit cast.

**Syntax formula:**
```java
// Implicit (automatic, safe — smaller type fits into larger):
double d = someInt;

// Explicit (manual, may lose data — larger type into smaller):
int i = (int) someDouble;
```

**Key rules / gotchas:**
- Widening (`int` → `double`) is automatic since no data is lost
- Narrowing (`double` → `int`) truncates the decimal — `(int) 9.9` becomes `9`, not `10`

**Implementation notes:**
> Went deeper into narrowing overflow behavior — casting `130` to `byte` wraps around to a negative number (`-126`) rather than erroring, since `byte`'s range is -128 to 127. Also covered `int`↔`char` casting via Unicode values, and `String`↔number conversion (`String.valueOf()`, `Integer.parseInt()`).

---

### 5️⃣ `_5_ControlFlow.java`
**Concept:** Conditional branching

**Why it matters:** This is how a program makes decisions — nearly every non-trivial piece of logic you write depends on branching correctly.

**Syntax formula:**
```java
if (condition) {
    // ...
} else if (condition) {
    // ...
} else {
    // ...
}

switch (variable) {
    case value1 -> // ...
    case value2 -> // ...
    default -> // ...
}
```

**Key rules / gotchas:**
- `switch` requires the compared value to be a constant expression (`int`, `String`, `enum`, etc.)
- The arrow form (`->`) avoids fall-through bugs that the older `case: ... break;` syntax was notorious for

**Implementation notes:**
> Covered both traditional `switch` (with `break`, including a demonstrated fall-through bug) and the modern arrow-style `switch` expression. Also noted that Java protects against the classic `if (x = 10)` assignment-vs-comparison typo bug at compile time, unlike C/C++.

---

### 6️⃣ `_6_Loops.java`
**Concept:** Repetition — `for`, `while`, `do-while`

**Why it matters:** Loops are how you process collections, repeat calculations, or wait for a condition — foundational for everything from array traversal to game loops later on.

**Syntax formula:**
```java
for (int i = 0; i < n; i++) { }

while (condition) { }

do { } while (condition);
```

**Key rules / gotchas:**
- `for` is best when you know the iteration count in advance
- `while` checks the condition *before* running the body — it may run zero times
- `do-while` checks *after* — it always runs at least once

**Implementation notes:**
> Also covered nested loops (multiplication table), `break` vs `continue`, for-each loops, intentional vs accidental infinite loops, and labeled breaks for exiting nested loops directly.

---

### 7️⃣ `_7_Arrays.java`
**Concept:** Fixed-size collections — 1D and 2D arrays

**Why it matters:** Arrays are Java's most basic data structure and a prerequisite for understanding the Collections Framework (`02-oop` → `03-collections`), which wraps and extends this same idea.

**Syntax formula:**
```java
int[] arr = new int[5];
int[] arr2 = {1, 2, 3};
int[][] grid = new int[3][3];
```

**Key rules / gotchas:**
- Array size is fixed at creation — you can't grow or shrink it (that's what `ArrayList` later solves)
- Arrays are zero-indexed; accessing an out-of-range index throws `ArrayIndexOutOfBoundsException`

**Implementation notes:**
> Covered sum/average/max/min operations, 2D array looping with nested loops, and a key gotcha: assigning one array to another (`b = a`) copies the *reference*, not the contents — modifying `b` also changes `a` unless you manually copy each element.

---

### 8️⃣ `_8_Strings.java`
**Concept:** String immutability, common `String` methods

**Why it matters:** Strings are everywhere in real programs, and Java's immutability model (every "modification" actually creates a new String) has real performance implications you'll need to understand once you hit loops that build strings repeatedly.

**Syntax formula:**
```java
String s = "text";
s.length();
s.substring(a, b);
s.charAt(i);
s.equals(other);
```

**Key rules / gotchas:**
- Use `.equals()` to compare String *content* — `==` compares object references and can silently give wrong results
- Strings are immutable: methods like `.substring()` return a *new* String rather than modifying the original

**Implementation notes:**
> Also covered the String Pool (`==` behaves inconsistently between literals and `new String()`), `split()`/`String.join()`, and `StringBuilder` for efficient mutable string building in loops.

---

### 9️⃣ `_9_Methods.java`
**Concept:** Reusable blocks of code — parameters, return types, overloading

**Why it matters:** Methods are the first step toward organizing code into reusable, testable units — the direct precursor to thinking in terms of classes and objects in `02-oop`.

**Syntax formula:**
```java
returnType methodName(paramType param1, paramType param2) {
    // ...
    return value;
}
```

**Key rules / gotchas:**
- `void` methods return nothing and need no `return` statement (or a bare `return;` to exit early)
- **Overloading** = same method name, different parameter lists — resolved at compile time based on argument types

**Implementation notes:**
> Also covered pass-by-value with primitives (no lasting effect outside the method) vs pass-by-value with arrays (content changes DO persist, since the copied reference still points to the same array), varargs (`int... nums`), and basic recursion with a factorial example.

---

### 🔟 `_10_UserInput.java`
**Concept:** Reading input from the console via `Scanner`

**Why it matters:** Nearly every interactive program (including the calculator and to-do app projects in this repo) needs to read user input — `Scanner` is the standard entry point for that in plain Java.

**Syntax formula:**
```java
import java.util.Scanner;
Scanner sc = new Scanner(System.in);
int x = sc.nextInt();
String s = sc.nextLine();
```

**Key rules / gotchas:**
- Mixing `.nextInt()` and `.nextLine()` is a classic bug: `.nextInt()` doesn't consume the trailing newline, so a following `.nextLine()` reads an empty string unless you clear it first

**Implementation notes:**
> Hit a real `InputMismatchException` while testing this firsthand — typed `"yes"` instead of `"true"` for a `nextBoolean()` prompt and crashed the program. Confirmed the fix works by validating input with `hasNextBoolean()` before reading. This became the motivating real-world example for why `04-exceptions` matters.

---

### 1️⃣1️⃣ `_11_OutputFormating.java`
**Concept:** Formatted console output — `printf`, `String.format`, text blocks

**Why it matters:** Raw `println` concatenation gets messy fast, especially for aligned numbers/tables or controlled decimal precision — `printf`-style formatting is the standard, readable way to control exactly how output looks.

**Syntax formula:**
```java
System.out.printf("%-10s %10.2f%n", name, price);
String msg = String.format("Hello %s, age %d", name, age);
```

**Key rules / gotchas:**
- `%.2f` **rounds**, it doesn't truncate
- Negative width (`%-10s`) left-aligns; positive width (`%10s`) right-aligns
- `%n` is the safer, OS-adaptive alternative to `\n` inside `printf`/`String.format`

**Implementation notes:**
> Covered format specifiers (`%s %d %f %c %b`), decimal precision control, field width/alignment, a practical aligned-table example, text blocks (`"""`) for multi-line strings, and comma-formatted large numbers (`%,d`).

---

## 🧠 Skills Demonstrated

Now that this folder is complete, it shows:
- Core Java syntax fluency (variables, control flow, loops, arrays, strings, methods)
- Understanding of Java's type system (static typing, casting rules, overflow behavior)
- Practical debugging experience (resolved a real `InputMismatchException` crash, a package-statement/Sources Root configuration issue, and array reference-copy gotchas)
- Ability to read/write clean, documented, single-purpose example programs
- A habit of writing developer-facing documentation alongside code

---

## 📝 How to Use This File

After completing each program:
1. Check its box in the **Progress Tracker** table above
2. Write a matching `.md` explanation file for that concept, breaking down the code line by line, and link it in the **Explanation** column
3. Replace its `Implementation notes` placeholder with 2–4 sentences on what the code does and what clicked (or didn't)
4. Commit the `.java` file, its `.md` explanation, and this updated `StudentGradeManager.md` together

This log feeds directly into the top-level portfolio `StudentGradeManager.md` once all phases are complete.

---

## ➡️ Next Up

`01-basics` is complete. `02-oop` is also now complete (all 14 topics — see [`concepts/02-oop/README.md`](../02-oop/README.md)). Currently working through **`03-collections`**.