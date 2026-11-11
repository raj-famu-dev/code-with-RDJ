# Chapter 1: Introduction to Computers, Programs, and Java

> Study notes for Chapter 1 of *Introduction to Java Programming* (Y. Daniel Liang). Written with Claude from the textbook chapter; the book is the source of truth.

## Contents

1. [Introduction](#11-introduction)
2. [What Is a Computer?](#12-what-is-a-computer)
3. [Programming Languages](#13-programming-languages)
4. [Operating Systems](#14-operating-systems)
5. [Java, the World Wide Web, and Beyond](#15-java-the-world-wide-web-and-beyond)
6. [Java Language Specification, API, JDK, JRE, and IDE](#16-java-language-specification-api-jdk-jre-and-ide)
7. [A Simple Java Program](#17-a-simple-java-program)
8. [Creating, Compiling, and Executing a Java Program](#18-creating-compiling-and-executing-a-java-program)
9. [Programming Style and Documentation](#19-programming-style-and-documentation)
10. [Programming Errors](#110-programming-errors)
11. [Developing Java Programs Using NetBeans](#111-developing-java-programs-using-netbeans)
12. [Developing Java Programs Using Eclipse](#112-developing-java-programs-using-eclipse)
13. [Chapter Summary: Quick Review](#chapter-summary-quick-review)
14. [Quick-Reference Cheat Sheet](#quick-reference-cheat-sheet)

---

## 1.1 Introduction
- **Programming** means creating (developing) software, also called a **program**.
- **Software** is the set of instructions that tells a computer or device what to do. It runs everything from PCs to airplanes, cars, phones, and toasters.
- There is no "best" language. Each has strengths and weaknesses, and experienced programmers learn many.
- The main skill is **problem solving**. Once you learn it in one language, others are easy to pick up.

## 1.2 What Is a Computer?
A computer is an electronic device that stores and processes data. It has **hardware** (the visible, physical parts) and **software** (the invisible instructions that control the hardware).

**Major hardware components** (connected by a **bus**, the "roads" that carry data and power, built into the **motherboard**):
1. CPU
2. Memory (main memory)
3. Storage devices (disks, CDs)
4. Input devices (keyboard, mouse)
5. Output devices (monitor, printer)
6. Communication devices (modem, NIC)

### 1.2.1 CPU (Central Processing Unit)
- The computer's "brain": it fetches instructions from memory and executes them.
- **Control unit**: controls and coordinates the other components.
- **Arithmetic/logic unit (ALU)**: does numeric operations (+, −, ×, ÷) and logical operations (comparisons).
- Built from silicon chips containing millions of **transistors** (tiny electric switches).
- **Clock**: emits pulses at a constant rate to synchronize operations. Higher clock speed means more instructions per unit of time.
  - Unit: **hertz (Hz)**, 1 pulse per second. Progression: Hz → MHz (1990s) → **GHz** (today, about 3 GHz).
- **Core**: the part of the processor that reads and executes instructions. **Multicore CPUs** have two or more independent cores for more processing power.

### 1.2.2 Bits and Bytes
- A computer is a series of switches that are on (1) or off (0).
- **Bit** = binary digit (0 or 1). **Byte** = 8 bits, the minimum storage unit.
- Small numbers (like 3) fit in one byte. Larger ones use several bytes.
- **Encoding scheme**: rules for translating characters and numbers into bits. Example: in **ASCII**, the character `C` = `01000011`.

| Unit | Approx. size |
|---|---|
| Kilobyte (KB) | 1,000 bytes |
| Megabyte (MB) | 1 million bytes |
| Gigabyte (GB) | 1 billion bytes |
| Terabyte (TB) | 1 trillion bytes |

Examples: a one-page document is about 20 KB (1 MB holds about 50 pages, 1 GB about 50,000). A two-hour HD movie is about 8 GB.

### 1.2.3 Memory (RAM)
- An ordered sequence of bytes that stores programs and the data they use. It is the computer's **work area**.
- A program and its data must be moved into memory before the CPU can execute them.
- Every byte has a **unique address**, used to store and retrieve data.
- Bytes can be accessed in any order, hence **RAM (random-access memory)**.
- Modern PCs typically have 4–8 GB of RAM.
- A byte is never empty, but its initial content may be meaningless. Its content is **lost when new data is placed in it**.
- Memory chips are simpler, slower, and cheaper than CPU chips.

### 1.2.4 Storage Devices
- Memory is **volatile**: data is lost when power is off. Storage devices hold programs and data **permanently**, and data is moved to memory when used (memory is much faster).
- A **drive** operates a medium. The **medium** physically stores the data.
- **Three main types:**
  - **Magnetic disk (hard disk) drives**: permanent storage, typically 500 GB to 1 TB. They can be internal or removable.
  - **Optical discs (CD and DVD)**:
    - CD-ROM is prepressed (read-only). CD-R is write-once. CD-RW is rewritable. A CD holds up to **700 MB**.
    - DVD (digital versatile disc) holds **4.7 GB**. Types are DVD-R and DVD-RW.
  - **USB flash drives**: small, portable storage that plugs into a USB port, available up to 256 GB.

### 1.2.5 Input and Output Devices
**Keyboard**
- **Function keys**: F1, F2, and so on. Their behavior depends on the software.
- **Modifier keys**: Shift, Alt, Ctrl. They change another key's action when pressed together.
- **Numeric keypad**: calculator-style keys on the right.
- **Arrow keys**: move the pointer or cursor.
- **Insert, Delete, Page Up, Page Down**: insert and delete text, move through a document by screen.

**Mouse**: a pointing device that moves the on-screen cursor and clicks objects.

**Monitor**
- **Screen resolution**: number of pixels horizontally × vertically (for example, 1,024 × 768). Higher resolution gives a sharper image.
- **Pixels**: "picture elements," the tiny dots that form the image.
- **Dot pitch**: space between pixels in mm. Smaller means sharper.

### 1.2.6 Communication Devices
- **Dial-up modem**: uses a phone line, up to 56,000 bps.
- **DSL**: uses a phone line, about 20× faster than dial-up.
- **Cable modem**: uses the cable TV line, generally faster than DSL.
- **NIC (network interface card)**: connects a computer to a **LAN** (local area network, such as a school, home, or office). 1000BaseT transfers 1,000 million bits per second (mbps).
- **Wireless adapter**: connects to a LAN or the Internet wirelessly.

## 1.3 Programming Languages
Computers don't understand human languages, so all programs must be converted into instructions the computer can execute.

### 1.3.1 Machine Language
- The computer's **native language**, which differs between computer types. It is a set of primitive instructions in **binary code**, for example `1101101010011010`.

### 1.3.2 Assembly Language
- Created because machine language is tedious and hard to read and modify.
- Uses short descriptive words called **mnemonics** (`add`, `sub`), for example `add 2, 3, result`.
- An **assembler** translates assembly code into machine code.
- It is a **low-level language**: close to machine language and machine dependent. Each assembly instruction corresponds to roughly one machine instruction, and you must know how the CPU works.

### 1.3.3 High-Level Language
- Emerged in the **1950s**. English-like, easy to learn, and **platform independent**: write once, run on different machines.
- Instructions are called **statements**, for example `area = 5 * 5 * 3.14159;`

**Popular languages (Table 1.1):**

| Language | Notes |
|---|---|
| Ada | Named for Ada Lovelace. Used in defense projects. |
| BASIC | Beginner's All-purpose Symbolic Instruction Code. |
| C | From Bell Labs. Combines assembly power with high-level ease and portability. |
| C++ | Object-oriented, based on C. |
| C# | Object-oriented, from Microsoft. |
| COBOL | Common Business Oriented Language, for business apps. |
| FORTRAN | FORmula TRANslation, for scientific and math apps. |
| Java | From Sun Microsystems (now Oracle). Object-oriented, platform independent. |
| JavaScript | Web language from Netscape. |
| Pascal | Named for Blaise Pascal. Used for teaching. |
| Python | Simple general-purpose scripting language. |
| Visual Basic | From Microsoft. Rapid Windows app development. |

- A program in a high-level language is **source code** or a **source program**. It must be translated into machine code by an interpreter or a compiler:
  - **Interpreter**: reads one statement, translates it, and executes it right away. A statement may become several machine instructions.
  - **Compiler**: translates the **entire** source program into a machine-code file, which is then executed.

## 1.4 Operating Systems
- The **OS** is the most important program on a computer. It manages and controls the computer's activities. Applications cannot run without an OS.
- Popular OSs: **Microsoft Windows, Mac OS, Linux**.
- Layers: User → Application Programs → Operating System → Hardware.

**Major tasks:**
1. **Controlling and monitoring system activities**: keyboard input, monitor output, tracking files and folders, controlling peripherals, keeping programs and users from interfering with each other, and security.
2. **Allocating and assigning system resources**: CPU time, memory, disks, and I/O devices.
3. **Scheduling operations**, using three techniques:
   - **Multiprogramming**: multiple programs run at once by sharing one CPU. The CPU is often idle while waiting on disks and other resources, so the OS lets other programs use it. Example: editing a file while the browser downloads.
   - **Multithreading**: a **single program** runs multiple tasks at once. Example: a word processor editing and saving at the same time.
   - **Multiprocessing**: multiple programs run concurrently on **multiple processors**. It is similar to multithreading, but across programs rather than within one.

## 1.5 Java, the World Wide Web, and Beyond
- Java was developed by a team led by **James Gosling** at **Sun Microsystems**. **Oracle** bought Sun in **2010**.
- It was originally called **Oak** and designed in **1991** for embedded chips in consumer electronics. In **1995** it was renamed Java and redesigned for web applications.
- Its appeal is **"write once, run anywhere."** Designer's description: simple, object oriented, distributed, interpreted, robust, secure, architecture neutral, portable, high performance, multithreaded, dynamic.
- It is a general-purpose language used for servers, desktops, and mobile devices. It was even used to control the Mars rover.
- **Applets** are Java programs that run in a web browser. They are **no longer allowed** in the latest Java due to security issues.
- Java is now popular for **server-side web applications** (processing data, generating dynamic pages).
- **Android** phone software is developed using Java.
- The **World Wide Web** is an electronic information repository accessed over the **Internet** (its infrastructure, over 40 years old).

## 1.6 Java Language Specification, API, JDK, JRE, and IDE
- **Java language specification**: technical definition of Java's syntax and semantics.
- **API (application program interface, also called the library)**: predefined classes and interfaces for building Java programs.
- **Three editions:**
  - **Java SE** (Standard Edition): client-side and desktop applications. **The book uses Java SE 8.**
  - **Java EE** (Enterprise Edition): server-side applications (servlets, JSP, JSF).
  - **Java ME** (Micro Edition): mobile devices.
- **JDK (Java Development Toolkit)**: programs, run from the command line, for compiling, running, and testing Java. For Java SE 8 it is **JDK 1.8 = Java 8 = JDK 8**.
- **JRE (Java Runtime Environment)**: the part that runs Java programs.
- **IDE (Integrated Development Environment)**: software that integrates editing, compiling, building, debugging, and help in one GUI. Examples: **NetBeans, Eclipse, TextPad**.
- NetBeans and Eclipse are **tools**, not different languages or dialects of Java.

## 1.7 A Simple Java Program

```java
public class Welcome {
  public static void main(String[] args) {
    // Display message Welcome to Java! on the console
    System.out.println("Welcome to Java!");
  }
}
```

**Key concepts:**
- **Console**: the text entry and display device. *Console input* is from the keyboard and *console output* is to the monitor.
- **Class**: every Java program has at least one. Class names conventionally **start with an uppercase letter**.
- **main method**: the **entry point** where execution begins. A class may contain several methods.
- **Method**: a construct that contains statements.
- **String**: a sequence of characters, enclosed in **double quotes**.
- **Statement terminator**: every statement ends with a **semicolon (;)**.
- **Reserved words (keywords)**: have specific meaning to the compiler and can't be used for other purposes. Examples: `class`, `public`, `static`, `void`.
- **Comments**: ignored by the compiler.
  - Line comment: `// text`
  - Block (paragraph) comment: `/* text */`
- **Blocks**: braces `{ }` group components. They can be nested. A class block contains data and methods, and a method block contains statements.
- **Special characters (Table 1.2):**

| Character | Name | Use |
|---|---|---|
| `{ }` | Braces | Denote a block |
| `( )` | Parentheses | Used with methods |
| `[ ]` | Brackets | Denote an array |
| `//` | Double slashes | Precede a comment line |
| `" "` | Quotation marks | Enclose a string |
| `;` | Semicolon | End of a statement |

**Tips and cautions:**
- Type the closing brace right after the opening one. IDEs do this automatically.
- Java is **case sensitive**: `main` ≠ `Main`.

**Other listings:**
- **Listing 1.2** prints three lines using three `println` statements.
- **Listing 1.3** computes `(10.5 + 2 * 3) / (45 – 3.5)`, which gives `0.39759036144578314`.
- **`print` vs. `println`**: `println` moves to the next line after output. `print` does not.
- The multiplication operator is `*`.

## 1.8 Creating, Compiling, and Executing a Java Program

**Workflow:**
1. Write source code in a `.java` file (the file name must **exactly match the public class name**, for example `Welcome.java`).
2. **Compile**: `javac Welcome.java`. This produces `Welcome.class` (**bytecode**) if there are no syntax errors.
3. **Run**: `java Welcome` (**do not** add `.class`, or the system looks for `Welcome.class.class`).
4. If there are compile errors, runtime errors, or wrong results, **modify, recompile, and re-run** (the process is repetitive).

**Key ideas:**
- **Bytecode** is a low-level, **architecture-neutral** code that runs on any platform with a **JVM (Java Virtual Machine)**.
- The **JVM** is a program, not a physical machine, that **interprets** bytecode one instruction at a time.
- Flow: Java source → (compiler) → bytecode → (JVM interpreter) → output. The JVM also runs library code.
- **Class loader**: loads the class's bytecode into memory (and other classes dynamically, just before they're needed).
- **Bytecode verifier**: checks the bytecode is valid and doesn't violate security restrictions.
- The JDK must be installed and configured first (Supplements I.B and I.C).
- You may use **packages** to organize programs (Supplement I.F).

**Errors at run time:**
- `NoClassDefFoundError`: the class file doesn't exist.
- `NoSuchMethodError`: there is no `main` method or it is mistyped (for example, `Main`).

## 1.9 Programming Style and Documentation
- **Programming style** is how a program looks. **Documentation** is the explanatory comments. Both reduce errors and improve readability.

**1.9.1 Comments**
- Begin with a **summary** of what the program does, its key features, and any unique techniques. Add comments for major steps and anything hard to read, and keep them **concise**.
- **Javadoc comments** (`/** ... */`) go before a class or method header and can be extracted into HTML with the `javadoc` command. Use `//` line comments for steps **inside** a method.

**1.9.2 Indentation and Spacing**
- Indent each nested component **at least two spaces**.
- Put **a space on both sides of a binary operator**: `3 + 4 * 4` (good), `3+4*4` (bad).

**1.9.3 Block Styles**
- **Next-line style**: opening brace on its own line. Braces align vertically and it is easy to read.
- **End-of-line style**: opening brace at the end of the line. It saves space and may avoid subtle errors. **The book uses it.**
- Both are acceptable, but be **consistent**.

## 1.10 Programming Errors

| Error type | Description | Difficulty |
|---|---|---|
| **Syntax (compile) errors** | Detected by the compiler. Examples: mistyped keyword, missing punctuation, unmatched brace. | Easy: the compiler shows where and why. |
| **Runtime errors** | Cause abnormal termination. Examples: invalid input, **integer division by zero** (`1 / 0`). | Not hard: the console shows the reason and location. |
| **Logic errors** | The program runs but gives the wrong result. | Hardest to find. |

- **Syntax example (Listing 1.4):** missing `void` before `main`, and a missing closing quote. Four errors were reported but there were only two causes. **Fix errors from the top down**, since early fixes can clear later errors.
- **Logic example (Listing 1.6):** `(9 / 5) * 35 + 32` gives **67** instead of **95**. **Integer division truncates**, so `9 / 5 = 1`. Use `9.0 / 5` (= 1.8).

**Common errors:**
1. Missing closing brace
2. Missing semicolon
3. Missing quotation mark
4. Misspelled names or wrong case (for example, `Main` instead of `main`, `string` instead of `String`)

## 1.11 Developing Java Programs Using NetBeans
**Create a project** (once):
1. File → New Project.
2. Select Java → Java Application → Next.
3. Enter the project name (for example, `demo`) and location. Uncheck "Use Dedicated Folder" and "Create Main Class."
4. Finish.

**Create a class:**
1. Right-click the project → New → Java Class.
2. Enter the class name (for example, `Welcome`), set Location to Source Packages, and leave Package blank (default package).
3. Finish, then type the code.

**Run:** right-click the file → **Run File** or press **Shift + F6**. It compiles automatically if changed, and output appears in the Output pane.

## 1.12 Developing Java Programs Using Eclipse
**Create a project:**
1. File → New → Java Project.
2. Enter the project name (for example, `demo`).
3. Select **"Use project folder as root for sources and class files"** so the `.java` and `.class` files are together.
4. Finish.

**Create a class:**
1. File → New → Class.
2. Enter the name, and check `public static void main(String[] args)`.
3. Finish to generate the template.

**Run:** right-click the class → Run → **Java Application**. Output appears in the Console pane.

## Chapter Summary: Quick Review
- A computer stores and processes data. It has hardware and software.
- The CPU is the brain. Memory is volatile. Storage is permanent.
- Computers use 0s and 1s because digital devices have **two stable states**.
- Bit = 0 or 1. Byte = 8 bits. A terabyte is about 1,000 gigabytes.
- Machine language → assembly language → high-level language. A **compiler** translates source into machine code.
- The OS manages and controls the computer.
- Java is platform independent. The source file must match the public class name and end in `.java`. Each class compiles to its own `.class` file.
- Compile with `javac`, run with `java`.
- Every Java program is a set of class definitions and needs a `main` method to run.
- Statements end with `;`. Blocks use `{ }`. Keywords are reserved. Comments are ignored. Java is case sensitive.
- Three error types: **syntax, runtime, logic**.

## Quick-Reference Cheat Sheet

| Concept | Remember |
|---|---|
| Source file extension | `.java` |
| Bytecode extension | `.class` |
| Compile command | `javac Welcome.java` |
| Run command | `java Welcome` (no `.class`) |
| Entry point | `public static void main(String[] args)` |
| Print without newline / with newline | `print` / `println` |
| Line comment / block comment / javadoc | `//` / `/* */` / `/** */` |
| Integer division | `9 / 5 = 1` (truncates) |
| Error types | Syntax (compiler), runtime (crash), logic (wrong output) |
