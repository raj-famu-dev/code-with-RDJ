# 🧩 c-by-RDJ — Complete Study Notes

> One consolidated reference covering every topic in this lab, with detailed explanations.
> Source: the completed concept folders (`01-basics` through `05-data-structures-in-c`) — all 40 topics.
> Status key matches the folder READMEs: ✅ completed · ⬜ not started.

---

## 📑 Table of Contents

1. [Module 01 — C Basics](#module-01--c-basics)
2. [Module 02 — Pointers & Memory](#module-02--pointers--memory)
3. [Module 03 — Structs & Modularity](#module-03--structs--modularity)
4. [Module 04 — Files & Systems](#module-04--files--systems)
5. [Module 05 — Data Structures in C](#module-05--data-structures-in-c)
6. [Pending Projects](#pending-projects)

---

# Module 01 — C Basics

*Folder:* [`concepts/01-basics`](./concepts/01-basics) · ✅ Complete · **9 topics**

### 1. Hello World & Compilation
C compiles straight to native machine code — no JVM, no runtime. The four stages of `gcc`:
1. **Preprocess** — expand `#include` and `#define` (`gcc -E`)
2. **Compile** — C to assembly (`gcc -S`)
3. **Assemble** — assembly to an object file `.o` (`gcc -c`)
4. **Link** — object files + standard library → executable
- `int main(void)` — `int` because the exit status goes to the shell; `(void)` because empty `()` in C means *unspecified* parameters.
- `return 0;` = success; `echo $?` shows it. Reaching the end of `main` without a return also returns 0 (C99+).
- `sizeof` is a compile-time **operator**, printed with `%zu` (the format for `size_t`).

### 2. Variables & Data Types
C is statically typed, but type sizes are the machine's choice — the standard guarantees only minimums and an ordering. Java's `int` is always 32 bits; C's is "at least 16".

| Type | Typical size | Notes |
|---|---|---|
| `char` | 1 byte | signedness is implementation-defined |
| `short` / `int` / `long` | 2 / 4 / 8 bytes | minimums, not exact |
| `float` / `double` | 4 / 8 bytes | |
| `bool` | 1 byte | needs `<stdbool.h>` |

- **Fixed-width types** (`<stdint.h>`): `int8_t`, `int32_t`, `int64_t`, `uint8_t` — exactly sized on every platform; what file formats, protocols and kernels use.
- `<limits.h>` publishes the platform's ranges (`INT_MAX`, `INT_MIN`, `UINT_MAX`, `CHAR_BIT`).
- `unsigned` drops the sign bit: no negatives, double the positive max, and **wraparound is defined** (modular arithmetic).
- Format specifiers: `%d`, `%ld`, `%lld`, `%u`, `%f`, `%c`, `%zu` — a mismatch between specifier and argument is **undefined behavior**.

### 3. Operators & Casting
- `7 / 2 == 3` — integer division truncates; one operand must be `double` for `3.5`.
- `(double)7 / 2` — the cast binds tighter than `/`; casts are explicit and unchecked.
- **Integer promotion:** two `char`s are promoted to `int` *before* the arithmetic — `char + char` cannot overflow.
- **Unsigned wraparound is defined** (`UINT_MAX + 1 == 0`) — a legitimate tool for hashing and timers.
- **Signed overflow is undefined behavior** — the compiler may wrap, trap, or delete your code path. Never write `i + 1 < i` overflow checks with signed types.

### 4. Control Flow
- Conditions are plain integers: `0` is false, anything else is true. `if (x = 5)` is an assignment that's always true — the classic bug.
- `switch` works only on integer types (`int`, `char`, `enum`) — **no strings, no ranges**. Cases are compile-time constant *labels*.
- **Fall-through:** without `break`, control runs into the next case. Grouping cases (`case 6: case 7:`) is idiomatic; accidental fall-through is the classic bug (`-Wimplicit-fallthrough` catches accidents).
- Always include `default` for unhandled values.

### 5. Loops
- `for (init; cond; update)` — init scoped to the loop since C99; any clause may be empty (`for (;;)` = infinite loop).
- `while` checks first (may run zero times); `do-while` runs at least once — note the trailing `;`.
- `continue` jumps to the condition (`while`) or the update clause (`for`); `break` exits the loop.
- C has **no labeled break** — `break` only escapes the innermost loop.

### 6. Arrays
Fixed-size, contiguous, and **completely unchecked** — no `.length`, no exception on a bad index.
- The length idiom: `sizeof a / sizeof a[0]` — works only where the *array* is visible; once it decays to a pointer, `sizeof` gives the pointer's size (8).
- Partial initializers zero the rest; designated initializers (`{ [2] = 30 }`, C99) set by index and zero everything else.
- `int grid[2][3]` — one contiguous block, row-major; `grid[1][2]` is the 6th int.
- **Out of bounds is undefined behavior** — no check, ever; ASan catches it at runtime.
- Avoid VLAs (`int a[n]` with runtime `n`) — optional since C11.

### 7. Strings & `<string.h>`
C has **no string type**: a "string" is a `char` array ending in a `'\0'` byte. Every buffer-overflow security bug in history lives at this boundary.
- `strlen` counts *before* the `'\0'`; `sizeof` counts *all* bytes — on a `char *` to a literal, `sizeof` gives the pointer (8).
- `strcpy`/`strcat` **don't know the destination's size** — the buffer overflow. `snprintf` is the modern safe copy.
- `strcmp` returns **0 when equal** (inverted from intuition); `strncmp` is bounded.
- `strchr`/`strstr` return a pointer *into* the string or `NULL` — always check.
- `gets()` was removed from C11; use `fgets`.

### 8. Functions & Prototypes
- C only has **pass-by-value**. There is no pass-by-reference — you pass an address *by value*, and the function follows it.
- `swap_fail(a, b)` swaps copies; `swap_works(&a, &b)` follows addresses to the caller's actual storage — the idiom for every out-parameter.
- Prototypes let the compiler type-check calls made before the definition; calling an undeclared function is a compile error in C99+.
- `void f()` means *unspecified* parameters; write `void f(void)` for "none".

### 9. Formatted I/O
- `printf` returns the character count (or negative on error) — almost always ignored, but it matters on files and sockets.
- Widths and flags: `%5d` (right-align), `%-5d` (left), `%08.3f` (zero-pad, 3 decimals), `%.4s` (truncate string).
- **The safe input pattern:** `fgets(line, sizeof line, stdin)` then `sscanf(line, "%d %31s %lf", ...)` — bounded, with `%31s` capping the string and the return count validating the parse.
- `scanf("%s")` without a width writes unbounded input into a bounded array — an overflow; `scanf` also needs `&` on everything except arrays.
- Never `fflush(stdin)` — undefined; flush output, not input.

---

# Module 02 — Pointers & Memory

*Folder:* [`concepts/02-pointers-and-memory`](./concepts/02-pointers-and-memory) · ✅ Complete · **8 topics** · clean under ASan + UBSan

### 1. Pointers & Addresses
A pointer is a variable whose value is a **memory address**. `&` takes an address; `*` follows one.
- `int *p = &x;` — read right-to-left: "p is a pointer to int". `*p = 99` writes `x` — one storage, two names.
- All object pointers are the same size (8 bytes on 64-bit); the *type* tells the compiler what's at the far end.
- `NULL` means "no object" — check before dereferencing. Uninitialized (garbage) pointers are worse than NULL.
- `int **pp` — pointer to a pointer; `argv` is exactly this shape.
- `int* a, b;` — only `a` is a pointer; the asterisk binds to the name.

### 2. Pointer Arithmetic
`p + 1` moves by **one element**, not one byte — the foundation of every loop over a buffer.
- The array name **decays** to a pointer to its first element; `a[i]` is *defined* as `*(a + i)` (which is why `2[a]` compiles).
- Pointer subtraction yields the **element count** (`ptrdiff_t`, printed with `%td`).
- One-past-the-end (`a + n`) is legal to compute and compare — **dereferencing it is UB**. That's why `p < a + n` is correct and `<=` is a bug.

### 3. Arrays & Pointers
Arrays and pointers are not the same thing — an array **decays** into a pointer in almost every context, and the decay loses the length.
- `sizeof a` is the exception where decay does *not* happen — which is why the length idiom works, but only in the scope where the array itself is visible.
- The C contract: **pointer + size** — every function that takes an array also takes its length. Forgetting the size half is how buffer overruns are born.
- `int grid[2][3]` is one contiguous block (2-D decay is one level deep); `int *m[2]` is a jagged array of pointers — what `char *argv[]` is.
- `int *p[3]` (array of pointers) vs `int (*p)[3]` (pointer to an array) — parentheses matter.

### 4. Strings as Char Pointers
| Spelling | Storage | Who frees it |
|---|---|---|
| `char s[] = "x"` | stack (copied) | automatic — scope exit |
| `const char *p = "x"` | static, read-only | never (program lifetime) |
| `char *p = malloc(...)` | heap | **you** — `free(p)` |

- Writing to a literal (`char *p = "x"; p[0] = 'y';`) is undefined behavior — literals live in read-only storage.
- Identical literals *may* be deduplicated by the compiler; never rely on pointer comparison between them.

### 5. Stack vs Heap
The stack: automatic, scoped, freed for you, small (MBs). The heap: requested with `malloc`, freed by **you** — the skill Java's GC does for you.
- `malloc(n * sizeof *p)` — returns `void *` or **NULL on failure** (always check). `sizeof *p` (the dereferenced pointer) keeps the expression correct even if the type changes.
- `calloc(n, size)` = malloc + zeroed. `realloc` grows/shrinks and **may move the block** — assign to a temporary, keep the original valid on failure.
- The discipline: `free(p); p = NULL;` — `free(NULL)` is a defined no-op, so a double-free of a NULLed pointer is harmless; a double-free of a live pointer is UB.
- Every `malloc` without a matching `free` on *every* exit path leaks; LeakSanitizer reports them at exit.

### 6. Memory Bugs & Sanitizers
The four classic heap bugs, each shown safe and (with `--trigger`) buggy under the sanitizers:
1. **Use-after-free** — the block is gone, the pointer still holds the address; ASan: `heap-use-after-free`.
2. **Heap-buffer-overflow** — `q[3]` in a 3-element block; ASan's redzones catch it on the spot.
3. **Memory leak** — no `free` on some path; LeakSanitizer reports at exit with the allocation's stack trace.
4. **Double-free** — corrupts allocator bookkeeping; glibc aborts, ASan says `attempting double-free`.
- **Reading a sanitizer report:** the bug type, the faulting line (`#0`), and the allocation site (`allocated by`) with its line. ASan tells you a story: who allocated it, who broke it, where.

### 7. Const & Void Pointers
| Declaration | Read as | You may |
|---|---|---|
| `const int *p` | pointer to const int | move `p`, not write `*p` |
| `int *const p` | const pointer to int | write `*p`, not move `p` |
| `const int *const p` | const pointer to const | neither |

- `const` binds to what's on its **left**; leading `const` binds right. This one rule decodes every C declaration.
- `void *` holds any object's address — the mechanism behind `malloc`, `memcpy`, `qsort`. But you cannot dereference it or do arithmetic on it: it's a **shipment box** — cast back before use.
- `malloc` returns `void *`, so `int *p = malloc(...)` needs no cast in C (C++ requires one).

### 8. Memory Ownership Patterns
For every allocation: who frees it, on which path? The three idioms of real C codebases:
1. **The `goto cleanup` ladder** (the Linux kernel's house style): every pointer starts NULL, every failure jumps to one exit, which frees **in reverse order of allocation** — safe because `free(NULL)` is a no-op. The one sanctioned use of `goto`.
2. **Ownership transfer** — `make_copy` returns the pointer; the caller now owns it. The contract lives in naming (`make_`/`dup_`) and documentation.
3. **Borrowing** — `const T *` parameters use memory they didn't allocate and free nothing. Most functions should be borrowers.
- The three rules: every allocation has exactly **one owner**; the owner frees on **every** exit path; borrowers never free.
- Returning a pointer to a stack local is the classic dangling pointer — transfer must be heap memory.

---

# Module 03 — Structs & Modularity

*Folder:* [`concepts/03-structs-and-modularity`](./concepts/03-structs-and-modularity) · ✅ Complete · **8 topics**

### 1. Structs
`struct` — C's record type: named fields of different types, the "fields, no methods" ancestor of the Java class.
- `struct student c = a;` copies **all bytes** — independent copies (unlike arrays, which decay). Pointer members copy the address (shallow copy).
- Designated initializers (`{ .id = 202 }`, C99) set by name and **zero everything unmentioned** — `struct options o = {0};` is the idiom.
- **Padding:** the compiler inserts alignment holes — `int + char[24] + double` = 36 used, but `sizeof` gives 40. Never compute struct sizes by hand; `offsetof` (from `<stddef.h>`) shows each field's real offset.
- Comparing structs with `==` is illegal — compare member by member.

### 2. Typedef
An **alias**, not a new type — nothing is wrapped, nothing is checked.
- `typedef struct { ... } Point;` — the most common spelling; the tag is required only for self-referential structs (linked-list nodes).
- Typedef'd pointers hide pointer-ness (`typedef char *string_t;` then `string_t a, b;` gives two pointers) — prefer visible `char *`.
- `typedef struct A B;` before `struct A` is complete is the forward-declaration idiom for opaque types — C's "private class".

### 3. Nested & Arrays of Structs
- `Book shelf[3]` — `3 * sizeof(Book)` contiguous bytes: C's table layout, cache-friendly, no pointer chasing.
- Nested initializers brace to match the struct; access chains left to right (`shelf[0].published.year`).
- Sorting an array of structs by hand: selection sort with whole-struct swaps (`Book tmp = shelf[i];`) — trivial because of value semantics.
- Middle insertion moves whole records (O(n) copies) — an array of *pointers* to structs trades locality for cheap moves.

### 4. Passing Structs
| Situation | Use |
|---|---|
| Small struct, want a copy | by value |
| Function must modify the caller's struct | pointer |
| Bigger struct, read-only | `const T *` (the default) |
| Ownership transfer (heap object) | `T *` returned/stored, documented |

- By value copies all bytes (a 10 KB struct in a hot loop is a performance bug); by pointer is 8 bytes and writable.
- `v->x` — the **arrow operator** — is `(*v).x` in one stroke. `.` for structs, `->` for pointers; mixing them is a compile error.
- Returning a pointer to a local struct is a dangling pointer — return by value or use the heap.

### 5. Unions
All members stored **in the same bytes** — an overlay. `sizeof` is the largest member; only the member last written is valid.
- The **tagged union** is the pattern behind every C interpreter/parser/database: an enum `kind` says which union member is valid; switch on the tag, read the matching member. C's answer to subclasses or `std::variant` — same idea, manual tag.
- Reading a member other than the last written is not a compile error and often not even a crash — you get garbage. The tag is the only truth.
- Type punning through a union is formally UB outside `memcpy`/`char` views — the safe route is `memcpy` between differently-typed objects.

### 6. Enums & Bitfields
- An enum constant is just an **`int`** — documentation, not type safety; `42` where an `enum status` is expected compiles. `switch` on an enum + `-Wswitch` warns about unhandled cases.
- Bitfields: `unsigned mode : 2;` — width in **bits**, packed by the compiler (`sizeof` 4 bytes, not 12 × 4). They **truncate silently**: `priority = 9` in a 3-bit field stores 1.
- The powers-of-two enum + OR-mask idiom: `CAP_READ = 1, CAP_WRITE = 2, CAP_EXEC = 4`; combine with `|`, test with `(caps & CAP_READ) != 0`.
- Bitfield layout is **implementation-defined** — never write bitfield structs to disk or the network expecting portability; use explicit shifts and masks for wire formats.

### 7. Function Pointers
Functions live at addresses; a variable can hold that address — C's callbacks, dispatch tables, and the entire extensibility mechanism of the standard library.
- `int (*op)(int, int)` — "op is a pointer to a function taking (int, int) returning int". The parentheses around `(*op)` are mandatory: `int *op(int, int)` is a *function returning int \**.
- The function's name decays to its address (no `&` needed); calling through the pointer uses normal call syntax.
- **The dispatch table** `int (*ops[4])(int, int)` replaces a `switch` with a table lookup — command handlers, state machines.
- The `qsort` comparator contract: two `const void *`, return **negative/zero/positive** for less/equal/greater. The overflow-safe idiom: `(x > y) - (x < y)` — never `return x - y` (overflows on extremes). The comparator must be a **strict weak ordering** or `qsort` reads out of bounds.

### 8. Headers & Linking
**Headers declare, source files define, the linker stitches.**
- The include guard (`#ifndef H / #define H / #endif`) makes double inclusion harmless.
- `extern int x;` declares without allocating; exactly one `.c` must define it. Zero definitions → "undefined reference" (a **linker** error); two → "multiple definition".
- `static` at file scope = **private to this translation unit** — C's `private`, how a module hides its state. (On a function: invisible outside the file.)
- Each `.c` is a translation unit compiled in isolation; the linker resolves symbols at the end. Change one file → recompile one object, relink — that incremental model is what `make` automates.
- Headers must hold *declarations* only, never plain definitions.

---

# Module 04 — Files & Systems

*Folder:* [`concepts/04-files-and-systems`](./concepts/04-files-and-systems) · ✅ Complete · **8 topics**

### 1. File Open & Close
- `FILE *` is an **opaque struct** — you hold a pointer, never see its fields. It owns a buffer, the OS file descriptor, and the error state.
- `fopen` returns **NULL on failure, not an exception** — the NULL check is not optional. `perror` prints the reason from `errno`.
- `fclose` returns a value too (the flush can fail) — a clean exit on unflushed data is a lie. Double `fclose` and use-after-close are UB.
- Modes: `"r"` (must exist), `"w"` (**truncates** — the most destructive two characters in the library), `"a"` (append), `"r+"/"w+"/"a+"` (read+write), `b` suffix (binary).
- The canonical line-reading loop: `while (fgets(line, sizeof line, in) != NULL)` — bounded, stops at newline (kept!), NULL at EOF.

### 2. Text I/O
The text-file trio: write with `fprintf`, read with `fgets`, parse with `sscanf` — each layer bounded and checked.
- `sscanf` returns the number of successful conversions — 3 means every field landed; **never use the variables after a short parse**.
- `%31[^,]` — "up to 31 chars that are not a comma": the bounded, CSV-safe alternative to `%s`.
- `scanf` needs `%lf` for `double` while `printf` uses `%f` — asymmetric and a classic bug.
- `fgets` **keeps the newline** — strip it with `line[strcspn(line, "\n")] = '\0';` or your last field has a hidden newline.
- Un-closed writes lose buffered bytes — the flush happens on `fclose`.

### 3. Binary I/O
`fread`/`fwrite` move raw bytes — no text formatting.
- `fwrite(&hdr, sizeof hdr, 1, f)`: source, **item size**, **item count**, stream — returns the item count; check it (a short read means EOF or error mid-item).
- The **magic number** pattern: a known constant at the head of the file (PNG: `89 50 4E 47`); if it doesn't match, fail fast instead of parsing garbage.
- A raw struct dump bakes in three machine assumptions: **padding**, **endianness**, and **sizes/alignment**. Real formats pin all three: fixed-width types, a declared byte order, field-by-field packing.
- `is_little_endian()`: store 1 as a 4-byte int; if the first byte in memory is 1, you're little-endian.

### 4. Errno & Exit Codes
C has no exceptions — failures are **return values**, and the details live in `errno`.
- Library functions **set `errno` on failure but never clear it on success** — check the return value first, *then* read `errno`. `if (errno)` as a success test is wrong on every platform.
- `strerror(errno)` maps the number to a message; `perror("prefix")` is the shortcut. The standard error line: **what you were doing, and why it failed**.
- Missing file → `ENOENT`; no permissions → `EACCES` — the same NULL return, distinguished only by `errno`.
- Exit codes are the process's verdict: 0 = success, 1 = runtime failure, 2 = usage error (bad user input) — the convention your Python scanner uses too. Scripts and CI read `$?`.
- Errors go to `stderr`, not `stdout` — so `demo > out.txt` keeps them visible and pipelines don't swallow them.

### 5. Command-Line Arguments
`int main(int argc, char **argv)` — arguments arrive as an array of C strings.
- `argv[0]` is the program name *as invoked* (use it in usage messages); `argv[argc]` is guaranteed NULL — the array is NULL-terminated like every good C array.
- Everything is **text**: `"21"` is two characters until you parse it. The safe parse: `strtol(argv[2], &end, 10)` — `end == argv[2]` means nothing parsed; `*end != '\0'` means partial garbage. `atoi("abc")` silently returns 0 — no error, just wrong.
- Usage errors exit **2**, runtime failures exit 1 — scripts can tell them apart.
- `argc < 3` check before indexing `argv[1]` — reading past the array otherwise.

### 6. Preprocessor & Macros
The preprocessor is a **text-substitution pass** before the compiler: `#include` pastes files, `#define` replaces names, `#if` deletes code at build time.
- **Macro arguments must be parenthesized, and the whole body too:** `MAX(a, b) * 2` with a bare body becomes `a > b ? a : b * 2`.
- Multi-statement macro bodies wrap in `do { ... } while (0)` — exactly one statement that expects a semicolon, safe under `if`.
- Predefined macros: `__FILE__`, `__LINE__`, `__DATE__`, `__TIME__` — the compiler's facts; `LOG_ERROR` logs location with zero runtime cost.
- `#if` deletes the untaken branch at build time — that's how debug logging and platform code work.
- `#x` stringifies; `a##b` concatenates tokens.
- Macros have **no type checking** and evaluate arguments on every use (`MAX(i++, j++)` increments twice). Prefer `static inline` functions whenever a macro isn't needed for types or tokens.
- `gcc -E -P file.c` shows the substitution — see what `#include` *actually does*.

### 7. Make & Builds
`make` reads rules that say **how** to build each file and **when** it needs rebuilding — the original incremental build system.
- A rule is **target: dependencies + TAB-indented recipe**. make's whole logic: rebuild if any dependency's *timestamp* is newer. Touch nothing → "Nothing to be done".
- The recipe **must** start with a real tab — spaces give `*** missing separator`, the most-asked make question in history.
- `.PHONY: all test sanitize clean` declares "always commands, never files" — otherwise a file named `test` makes the target look up to date.
- The repo's convention (matching `cpp-by-RDJ`): every Makefile exposes `make`, `make test`, `make sanitize` (the ASan/UBSan build), `make clean`.
- `clean` removes build products — artifacts never get committed; only sources do.

### 8. Flexible Array Members
A struct whose last field is an unsized array (`int items[];`) — one `malloc` allocates the header *and* the payload together.
- `sizeof(IntVec)` ignores the flexible member — it's a marker for "payload starts here". Size the record with `offsetof(IntVec, items) + n * sizeof(int)` (using `sizeof(struct)` is not guaranteed correct; `offsetof` is exact).
- **Forgetting the `+ n * sizeof(int)` is an instant heap overflow** — ASan catches it.
- The payload indexes directly (`v->items[i]`) — one allocation, one contiguous cache-friendly block, zero pointer chasing. Behind dynamic arrays, variable-length packets, and strings inside structs.
- Before C99 this was the famous "struct hack" (`int items[1];` + over-allocation).
- Copying the struct copies only the header — `memcpy` the whole block for a deep copy.

---

# Module 05 — Data Structures in C

*Folder:* [`concepts/05-data-structures-in-c`](./concepts/05-data-structures-in-c) · ✅ Complete · **7 topics** · clean under ASan + UBSan

### 1. Dynamic Array
The workhorse behind Python's `list`, Java's `ArrayList`, C++'s `std::vector` — built from scratch: a heap block, `count`, `capacity`, and **doubling** when full.
- The struct *is* the data structure: `data / count / capacity` — used vs allocated. `copies` is a measurement counter.
- When `count == capacity`: double and `realloc` (assign to a temporary — the block may move; the original stays valid on failure).
- **Measured in the repo:** 100,000 pushes from capacity 4 → ~131,000 element-copies ≈ **1.3 per push** — amortized O(1). The Java DSA module measured 1.31 copies/add with the JDK's ArrayList: same experiment, same answer.
- Growing by +1 instead of doubling is O(N²) total copies — the quadratic death of hand-rolled vectors.
- `data[i]` is O(1) — the array's superpower and the reason this is the default structure everywhere.

### 2. Linked List
Nodes chained by pointers, each a separate `malloc` — O(1) insert/remove when you hold the node; O(n) to find it. The doubly-linked version here matches Java's `LinkedList` design.
- The node is self-referential — the struct tag is required (Module 03's typedef lesson).
- `head` + `tail` + `count`: both ends O(1) (a queue for free); `count` avoids the O(n) length walk.
- **The four-pointer dance:** `n->prev = tail; tail->next = n;` — updating both directions is where bugs live ("works forward, breaks backward").
- The out-parameter pattern: `list_pop_front(List *, int *out)` — return value carries the error, the pointer delivers the data.
- `list_free`: stash `next` **before** `free` (reading `n->next` after is the Module 02 use-after-free). One malloc per node, one free per node.
- The structural tax: `list[i]` is i pointer-chases; `array[i]` is one load. Choosing list vs array is C's fundamental trade.

### 3. Stack & Queue
Two access disciplines built on what we already have.
- **Stack (LIFO)** on the dynamic array's end: push/pop at `data[count]` — O(1) by construction, no shifting ever. Popping an empty stack is a **reported condition** (return -1), not a crash.
- **Queue (FIFO)** as a **ring buffer**: keep a `head` index and wrap with modulo — the freed slot gets reused, data never moves, O(1) with zero shifting.
- The tail is computed `(head + count) % capacity` — no separate tail field to desynchronize.
- The classic ring-buffer bug: `head == tail` for both "empty" and "full" — the same condition; that's why `count` exists.
- Stack: undo, expression evaluation, DFS, call stacks. Queue: scheduling, BFS, buffering.

### 4. Hash Table
Keys hash to buckets, collisions chain — the same structure as Python's `dict` and Java's `HashMap`.
- **FNV-1a:** XOR each byte, multiply by the FNV prime — deterministic (required) and well-distributed. A bad hash degrades the table to a linked list.
- `fnv1a(key) & (capacity - 1)` — bitwise AND with power-of-two-minus-one is a cheap modulo; that's why real tables keep capacity a power of two.
- Insert at the chain's **head** — O(1), no tail tracking. Update-or-insert in one chain walk.
- The table owns each key **copy** (`strdup`) — storing the caller's `char *` makes keys dangle when the caller reuses them.
- **Measured in the repo:** 100 keys in 16 buckets (load factor 6.25) → every lookup walks ~6 entries — exactly the load factor, because FNV-1a spreads uniformly. The lesson: **the table is only as fast as the hash's spread and the load's bound.**
- Real tables **rehash into a bigger array** at ~0.75 load — every chain short again, at the cost of re-hashing everything once. Project 02 fixes this teaching version.

### 5. Sorting
Three sorters, one array, verified against each other (`memcmp`) — the repo's oracle method in miniature.
- `qsort(base, count, size, cmp)` — the library sorter: swaps elements as raw byte blocks (that's why it needs the element size), comparator gets `const void *`. The C++ `std::sort` lesson applies: templates beat the type-erased comparator.
- **Comparator contract:** negative/0/positive, consistent and transitive — `(x > y) - (x < y)` is overflow-safe; `return x - y` is the classic bug (`INT_MIN - 1` wraps and flips sign).
- **Quicksort (Lomuto):** partition with the last element as pivot; the pivot lands in its final sorted position; recurse both sides. Average O(n log n); **worst case O(n²) on sorted input** with this pivot — random pivot or median-of-three fixes it. Not stable.
- **Merge sort:** halve, recurse, merge two sorted runs (the two-finger walk); guaranteed O(n log n), needs O(n) extra space (`tmp`), stable (`<=` keeps order).
- The overflow-safe midpoint: `lo + (hi - lo) / 2`, never `(lo + hi) / 2`.

### 6. Searching
- **Linear:** correct on any data, O(n) — the honest default.
- **Binary:** needs **sorted** input, O(log n) — 10 elements ≈ 3.3 comparisons; a million ≈ 20. The half-open interval `[lo, hi)` with `mid = lo + (hi - lo) / 2` (the overflow-safe midpoint — the famous bug that lived in Java's standard library for years).
- **Binary search on unsorted data doesn't crash and doesn't warn — it silently returns garbage.** The precondition is a contract, not a suggestion.
- `bsearch(&target, base, n, size, cmp)` — the library version; sort with `qsort`, search with `bsearch`, one comparator serves both.

### 7. Testing in C
C has no built-in testing story — so this lab builds the same tiny harness used across the repo: **`N checks, 0 failed`** and exit code 0.
- The `CHECK` macro: `do/while(0)` for statement-safety, `#cond` stringification prints the *failed expression*, `__FILE__`/`__LINE__` for location. Counts and **continues** — one failure doesn't hide the rest.
- The exit code *is* the test result: `return checks_failed == 0 ? 0 : 1;` — a test binary that always exits 0 is decoration.
- **Seeded randomness** (xorshift32, seed 42): the same failures every run, every machine — the repo-wide rule (Java's `Random(42)`, C++'s `mt19937`, Python's `random.Random(42)`).
- **The oracle method:** test against an independent reference (here `strlen` vs `count_chars` on generated inputs) — the Java structure-vs-JDK and C++ structure-vs-`std` checks are this pattern at scale.
- **CHECK vs assert:** CHECK is a counted, reported outcome (keep running); `assert` aborts the process — for invariants, and it **compiles away with `-DNDEBUG`** (never put side effects inside one).

---

# Pending Projects

Both projects are ⬜ **not started** — READMEs and definitions of done written, no code yet (per the folder READMEs):

| Project | What it will be |
|---|---|
| [`project-01-grade-manager-c`](./projects/project-01-grade-manager-c) | The Java capstone ported to C17: a `Student` struct, a dynamic array grown with `realloc`, `fgets`+`sscanf` validation, text-file persistence with `errno` reporting, Makefile with `make test` / `make sanitize` |
| [`project-02-hash-table-c`](./projects/project-02-hash-table-c) | Module 05's hash table hardened into a real deliverable: separate chaining, FNV-1a, resize at load factor 0.75 with rehash, documented ownership, and an oracle test suite running thousands of seeded random operations against a reference |

---

## How to Study These Notes

1. **Predict** the output of a snippet before running it.
2. **Run** the matching file in the concept folder (`gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g`).
3. **Break** it on purpose (several files take a `--trigger` argument) and read the sanitizer report.
4. **Explain** the topic out loud in plain English — if you can't, reread the section.
5. **Ship**: the repo's own method — write, run, break, explain, ship.

*Consolidated from the completed files in this lab. Every claim here is checkable against the source files next to it.*

---

<div align="center">

<sub>Built and owned by [Raj Patel (RDJ)](https://github.com/raj-famu-dev) — Computer Science @ **Florida A&M University** · Tallahassee, Florida · [Instagram @rdj_369](https://instagram.com/rdj_369)</sub>

[⬅ c-by-RDJ](./README.md) · [Repository home](../README.md)

</div>
