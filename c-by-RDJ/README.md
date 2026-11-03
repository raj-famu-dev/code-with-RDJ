<div align="center">

# C Programming Lab

![C](https://img.shields.io/badge/C-C17-A8B9CC?style=for-the-badge&logo=c&logoColor=black)
![Modules](https://img.shields.io/badge/Concept%20Modules-5-0EA5E9?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Initial%20Scaffold-F59E0B?style=for-the-badge)

### *Understand the machine. Write clear C. Own your memory.*

[About](#-about) • [Method](#-learning-method) • [Curriculum](#-curriculum) • [Run It](#-run-it-yourself) • [Projects](#-projects)

[⬅ Back to repository](../README.md) · [Java Lab](../java-by-RDJ/README.md) · [C++ Lab](../cpp-by-RDJ/README.md)

</div>

---

## About

This is the C programming track in Raj Patel's (RDJ) public learning repository. It focuses on C17, the standard library, explicit memory management, data representation and systems-programming foundations.

C is treated as its own language, not as a smaller version of C++. This lab uses functions, structs, pointers, manual resource management and standard C facilities. It does not use C++ classes, references, templates or the STL.

## Learning Method

Every concept is paired with a source file and a Markdown walkthrough:

1. Read the concept and predict the output.
2. Compile with warnings enabled.
3. Run the program and compare actual output with the walkthrough.
4. Experiment with edge cases and invalid input.
5. Explain the code, memory behavior and trade-offs in your own words.

A topic is not marked complete merely because a file exists. Completion requires a local compile, a successful run and a reviewed walkthrough.

## Curriculum

| Module | Focus | Topics | Status |
|---|---|---:|---|
| [01-foundations](./concepts/01-foundations) | Program structure, types, operators, control flow, loops and I/O | 4 | ⬜ Verify locally |
| [02-functions-and-arrays](./concepts/02-functions-and-arrays) | Functions, prototypes, arrays and strings | 3 | ⬜ Verify locally |
| [03-pointers-and-memory](./concepts/03-pointers-and-memory) | Pointers, pointer arithmetic and dynamic allocation | 3 | ⬜ Verify locally |
| [04-structs-and-data-structures](./concepts/04-structs-and-data-structures) | Structs, enums, linked lists, stacks and queues | 3 | ⬜ Verify locally |
| [05-files-and-preprocessor](./concepts/05-files-and-preprocessor) | File I/O, headers, macros and debugging | 3 | ⬜ Verify locally |

**Initial scaffold:** 5 modules and 16 topic examples. All topics remain unverified until compiled and run locally.

## Run It Yourself

A C17 compiler is required. GCC and Clang are suitable.

    cd c-by-RDJ/concepts/01-foundations
    cc -std=c17 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -g _1_HelloWorldAndCompilation.c -o hello
    ./hello

The examples are separate programs and should be compiled individually because each has its own main function.

## Projects

| Project | Concepts combined | Status |
|---|---|---|
| [project-01-cli-calculator](./projects/project-01-cli-calculator) | Functions, input validation, operators and control flow | ⬜ Planned |
| [project-02-student-record-manager](./projects/project-02-student-record-manager) | Structs, arrays, functions and file I/O | ⬜ Planned |

## Integrity

This is an initial scaffold generated with AI assistance. The examples and walkthroughs have **not** been locally compiled, run or independently verified in this commit. Review, test and revise them before changing any status to completed. Do not claim measured results until they have been reproduced.

## Related Labs

| Lab | Focus |
|---|---|
| [Java](../java-by-RDJ/README.md) | OOP, collections, concurrency and backend foundations |
| [C++](../cpp-by-RDJ/README.md) | Memory ownership, modern C++, data structures and concurrency |
| [Python](../python-by-RDJ/README.md) | Automation, scripting, data work and networking |
| [Computer Networks](../computer-network-by-RDJ/README.md) | Protocols, network layers and runnable simulations |

---

<div align="center">

### Built and maintained by Raj Patel (RDJ)

Computer Science · Florida A&M University · Tallahassee, Florida

[⬅ Back to repository](../README.md) · [GitHub: raj-famu-dev](https://github.com/raj-famu-dev)

**© 2026 Raj Patel (RDJ).** Released under the [MIT License](../LICENSE).

</div>
