# ⚙️ cpp-by-RDJ — Complete Study Notes

> One consolidated reference covering every topic in this repository, with detailed explanations.
> Source: all 6 completed concept modules (49 topics) and the 3 completed projects.
> Every `.cpp` here builds with zero warnings under `g++ -std=c++20 -Wall -Wextra -Wpedantic`, runs with exit 0, and is clean under AddressSanitizer and UndefinedBehaviorSanitizer.

---

## 📑 Table of Contents

1. [Module 01 — Basics](#module-01--basics)
2. [Module 02 — Pointers & Memory](#module-02--pointers--memory)
3. [Module 03 — OOP](#module-03--oop)
4. [Module 04 — Templates & the STL](#module-04--templates--the-stl)
5. [Module 05 — Modern C++](#module-05--modern-c)
6. [Module 06 — Concurrency & Systems](#module-06--concurrency--systems)
7. [Project 01 — Data Structures From Scratch](#project-01--data-structures-from-scratch)
8. [Project 02 — Memory Safety Lab](#project-02--memory-safety-lab)
9. [Project 03 — Thread Pool](#project-03--thread-pool)

---

# Module 01 — Basics

*Folder:* [`concepts/01-basics`](./concepts/01-basics) · ✅ Complete · **9 topics**

### 1. Hello World & Compilation
- The **build model** is the first lesson: `g++ -std=c++20 -Wall -Wextra -Wpedantic -O0 -o demo file.cpp` — each source is compiled (preprocess → compile → assemble) and linked into a binary.
- `#include <iostream>` is textual inclusion; `int main()` is the entry point and its return value is the process exit code.
- The compilation flags this lab uses everywhere: `-Wall -Wextra -Wpedantic` (warnings on), `-std=c++20` (the standard), `-fsanitize=address,undefined` in the sanitizer builds.
- Java hides compilation behind `javac`; here you see the whole pipeline.

### 2. Variables & Types
- **Fixed-width integers:** `int8_t` … `int64_t`, `size_t` for sizes and indexes, `bool`, `char` (a byte, not a Unicode character), `float`/`double`, `auto` for inference.
- `int` has no guaranteed size — `int32_t` says exactly what you mean.
- **Initialization forms:** `int x = 5;`, `int x{5};` (braced — rejects narrowing: `int x{3.5};` fails to compile), `auto x = 5;`.
- `const` for compile-time-ish immutability, `constexpr` for true compile-time values (Module 05).

### 3. Operators & Casting
- The C casts are gone from the lab's style; use **named casts:** `static_cast<int>(d)` (checked conversion), `dynamic_cast<Derived*>` (checked downcast — returns nullptr on failure), `const_cast`, `reinterpret_cast`.
- Integer division truncates (`7 / 2 == 3`), `%` is remainder, and **signed overflow is undefined behavior** — the reason UBSan exists.
- `0.1 + 0.2 != 0.3` is a float lesson that bites every language.
- **Comparison:** `==` on floats needs an epsilon; C++ has no `===`.

### 4. Control Flow
- `if` / `else if` / `else`, `switch` on integers and enums — cases need `break`, fall-through is possible.
- **`if` with initializer (C++17):** `if (auto it = m.find(k); it != m.end())` — the variable lives only for the if/else.
- Ternary `cond ? a : b` is an expression; no pattern-matching switch (that's `std::variant` + `std::visit`, Module 05).

### 5. Functions
- **Pass by value copies; pass by reference (`T&`) aliases; pass by const reference (`const T&`) aliases read-only** — the single most important C++ function lesson. Big objects go by `const T&` unless you need to modify or own them.
- Default arguments, function overloading (resolved at compile time — no runtime dispatch like Java overriding).
- `auto` return type and trailing return syntax.
- **Header/implementation split:** declarations in headers, definitions in `.cpp` files, `inline` for header-defined functions.

### 6. Arrays & Vectors
- Raw `int a[10]` — fixed size, no bounds checks (out of bounds = undefined behavior, silently).
- **`std::vector<T>`** is the workhorse: growable, `push_back` amortized O(1), `size()`, `at()` (throws) vs `[]` (unchecked), range-for: `for (const auto& x : v)`.
- `reserve` to avoid reallocation, `resize` to change size.
- Vectors of vectors, and the cost model: contiguous memory = cache-friendly (unlike `std::list`).

### 7. Strings & `string_view`
- `std::string` — growable, owns its bytes; `+` concatenation, `substr` (copies!), `find` returns `npos`, `c_str()` for C interop.
- **`std::string_view`** — a non-owning slice of characters: cheap to pass, no allocation, but **dangles if the underlying string dies**. Take `string_view` parameters to avoid copies; never store one.
- Raw C strings (`const char*`) end at the first `'\0'` — the buffer overflows of the C world come from here.

### 8. Input & Output
- `std::cout << x << "\n";` — the stream operators; `std::cin >> x` for input (fails silently on bad input — check the stream state).
- `'\n'` vs `std::endl` (endl flushes; flushing every line is slow).
- Streams are chainable and type-safe, unlike C's `printf` (which this lab avoids).
- `std::getline(std::cin, line)` for whole lines (the `>>` leaves the newline behind, the Java-Scanner trap again).

### 9. Headers & Namespaces
- **The One Definition Rule (ODR):** a function may be declared many times but defined exactly once across the program — the reason headers hold declarations.
- Include guards (`#ifndef`/`#define`/`#endif`) and `#pragma once`.
- `namespace rdj { ... }` — logical grouping, `using namespace std;` is banned in headers (pollutes every includer).
- Compilation units and linking: undefined references are linker errors, not compiler errors.

---

# Module 02 — Pointers & Memory

*Folder:* [`concepts/02-pointers-and-memory`](./concepts/02-pointers-and-memory) · ✅ Complete · **8 topics** — the heart of the lab

### 1. Pointers & Addresses
- A pointer is a variable holding a **memory address**: `int* p = &x;`, dereference with `*p`.
- `nullptr` (never `NULL` or `0` in modern C++); `&` takes an address, `*` reads/writes through it.
- Pointer arithmetic steps by `sizeof(T)`: `p + 1` moves one *element*, not one byte.
- **The core difference from Java:** in Java every object variable is a managed reference; in C++ the pointer is raw — nobody but you guarantees it points at something alive.

### 2. References vs Pointers
- A **reference `int& r = x`** is an alias: no null, no re-seating, must be initialized, no `*` to use.
- A pointer can be null, reassigned, and do arithmetic — more flexible, more dangerous.
- API design: use references when "no object" is impossible; pointers (or `optional`) when absence is real.
- `const T&` is the standard read-only parameter; `T&&` is the move/rvalue reference (Module 05).

### 3. Stack vs Heap
- **Stack:** automatic storage — `int x;` lives until its scope ends; deallocation is free and instant.
- **Heap:** dynamic storage — `new` allocates, `delete` frees; you own the pairing. `new T[...]` pairs with `delete[]`.
- Stack objects destruct at scope exit — the foundation of RAII (topic 5).
- Stack is small (MBs), fast, LIFO; heap is large, slower, and **you manage it**.

### 4. Memory Bugs & Sanitizers
- The bug classes: **use-after-free, heap-buffer-overflow, leak, double-free, stack-buffer-overflow, uninitialized read** — each with a toy demo (deliberately buggy, behind an explicit `--trigger` flag).
- **AddressSanitizer (ASan)** instruments every allocation with redzones and reports the exact bug, file and line; **LeakSanitizer** reports leaks at exit; **UBSan** catches undefined behavior (overflow, bad casts).
- Compile with `-fsanitize=address,undefined -g` and the tool tells you what you broke — this is the skill the whole lab builds toward.
- A later project (memory-safety lab) runs every one of these bugs and captures the real sanitizer output.

### 5. RAII
- **Resource Acquisition Is Initialization:** the resource's lifetime *is* the object's lifetime — the constructor acquires, the destructor releases.
- `std::lock_guard` (unlocks in its destructor), `std::fstream` (closes on destruction), every smart pointer.
- No `finally`, no `close()` you can forget — the compiler calls destructors on every exit path, including exceptions.
- RAII is C++'s answer to Java's GC + try-with-resources, but with deterministic timing and zero runtime cost.

### 6. Smart Pointers
- **`std::unique_ptr<T>`** — sole owner, moves only (`std::move`), zero overhead, deletes on destruction. The default choice.
- **`std::shared_ptr<T>`** — reference-counted shared ownership; `make_shared` allocates object + counter together; thread-safe counting, not thread-safe object.
- **`std::weak_ptr<T>`** — non-owning observer that breaks `shared_ptr` cycles (`lock()` returns a `shared_ptr` or null).
- Rules: never raw `new`/`delete` in application code; pass `unique_ptr` by value to transfer ownership; `make_unique`/`make_shared` over constructor calls.

### 7. Rule of Three/Five/Zero
- **Rule of Three:** if you write a destructor, copy constructor, or copy assignment, you probably need all three.
- **Rule of Five (C++11):** add move constructor and move assignment.
- **Rule of Zero:** write none of them — use members that manage themselves (`unique_ptr`, `vector`, `string`), and the compiler's defaults are correct.
- The classic bug: a raw-pointer class with default copy = two objects deleting the same memory (double free).

### 8. `const` & Lifetimes
- `const T` value, `const T&` reference, `T* const` (const pointer), `const T*` (pointer to const) — read the type right to left.
- `constexpr` — computed at compile time.
- **Dangling references:** returning `const T&` to a local = undefined behavior; a `string_view` outliving its string; `auto&` to a temporary.
- Tools: lifetime analysis in the compiler, and ASan to catch what slips through.

---

# Module 03 — OOP

*Folder:* [`concepts/03-oop`](./concepts/03-oop) · ✅ Complete · **9 topics**

### 1. Classes & Structs
- `class` and `struct` are identical **except default access**: `class` private, `struct` public.
- Members declared in the class; objects created automatically on the stack or with `new` — no garbage collector.
- **No packages/visibility keywords beyond `public`/`protected`/`private`** — access control is per-class, not per-file like Java.

### 2. Constructors & Destructors
- Constructors: default, parameterized, member-initializer list (`: x_(x), y_(y)` — the *only* correct way to init `const` and reference members), `explicit` to block implicit conversions.
- **Destructors (`~T()`)** run at scope exit or `delete` — deterministic, unlike Java's GC.
- Delegation `T() : T(args) {}`; `= default` and `= delete` to control the defaults.

### 3. Encapsulation
- Private data + public methods, same as Java; getters return `const T&` to avoid copies.
- The **header is the interface**: users see the class layout, so changing private members is an ABI break (the pimpl idiom exists for this).
- `friend` functions/classes — controlled access, used for operators and tests.

### 4. Inheritance
- `class Dog : public Animal` — public inheritance is "is-a"; the base's constructor runs first.
- **No `super` keyword** — the base is named: `Animal::speak()`.
- Slicing: `Dog d = baseDog;` copies only the `Animal` part — a classic trap that Java cannot have.

### 5. Virtual Functions & Polymorphism
- `virtual` enables **runtime dispatch via the vtable**; `override` marks intent; `final` blocks further overriding.
- **The rule:** a base class destructor must be `virtual`, or `delete basePtr` leaks the derived parts.
- Virtual calls cost one indirection (vptr → vtable → function); constructors can't be virtual.
- This is the mechanism Java uses for *every* method by default — C++ makes you opt in.

### 6. Abstract Classes & Interfaces
- A pure virtual: `virtual void draw() const = 0;` — makes the class abstract; can't instantiate.
- An interface in C++ = a class of only pure-virtual functions (no `interface` keyword).
- The override checker: missing `override` on a typo'd signature silently creates a *new* virtual function.

### 7. Operator Overloading
- Define `operator+`, `operator==`, `operator<<` as member or free functions; `operator<<` for streams must be a free function.
- **Rule of thumb:** overload operators only when the meaning is natural (a `Vec2` with `+`), keep semantics consistent (`+` shouldn't mutate).
- `operator==` should match `operator<=>` (spaceship, C++20) or be defined alongside a matching `operator<` for ordered containers.
- `std::hash` specialization for custom keys in `unordered_map` (Module 04).

### 8. Static & Nested Members
- `static` members belong to the class — declared in the header, **defined in exactly one .cpp file** (ODR again).
- Static member functions have no `this`; `inline static` members (C++17) can live in the header.
- Nested classes/structs, and the **singleton** done correctly: `static T& instance() { static T t; return t; }` — thread-safe construction guaranteed by the standard.

### 9. Composition vs Inheritance
- Same lesson as Java: prefer has-a; composition in C++ is a *member object* whose lifetime is automatic (RAII again).
- Inheritance couples you to the base's layout; a member is swappable and testable with fakes.
- Private inheritance = "implemented-in-terms-of" — rare, and a smell when composition works.

---

# Module 04 — Templates & the STL

*Folder:* [`concepts/04-templates-and-stl`](./concepts/04-templates-and-stl) · ✅ Complete · **8 topics**

### 1. Function & Class Templates
- `template <typename T> T max(T a, T b)` — the compiler *generates* a version per type used (compile-time generics, not Java's erased generics).
- Class templates: `template <typename T> class Box { T value; };` used as `Box<int>`.
- Template argument deduction, explicit instantiation, and member functions defined outside the template.
- **Java contrast:** no type erasure — `Box<int>` and `Box<string>` are genuinely different generated classes, with real, checkable types at runtime.

### 2. Concepts & Constraints (C++20)
- `template <typename T> requires std::integral<T>` — or the shorthand `void f(std::integral auto x)`.
- Concepts replace SFINAE with readable, named constraints; error messages say "T doesn't satisfy X" instead of a wall of template noise.
- Standard concepts: `std::integral`, `std::floating_point`, `std::input_iterator`, `std::equality_comparable`, `std::default_initializable`.
- This is the modern way — SFINAE (topic 8) is the legacy technique you still read in old code.

### 3. Sequence Containers
- `vector<T>` — contiguous, amortized O(1) push_back, the default; `array<T, N>` — fixed-size, stack-friendly.
- `list<T>` — doubly-linked, O(1) splice, terrible cache locality; `forward_list` — singly-linked.
- `deque<T>` — double-ended, chunked; **the choice rule:** need index access → `vector`; need push_front → `deque`; almost never `list`.
- `std::span` (C++20) — a non-owning view over any contiguous range (Module 05).

### 4. Associative Containers
- `map<K,V>` / `set<K>` — sorted (red-black trees), O(log n), iterators walk in order.
- `unordered_map` / `unordered_set` — hash tables, O(1) average; need `std::hash<K>` or a custom hash.
- **`[]` on `map` inserts a default value if missing** — a silent bug factory; use `at()` or `find()` when you don't want that.
- Choosing: ordered iteration or range queries → map; pure lookup → unordered_map.

### 5. Iterators & Algorithms
- Iterators are the glue: `begin()`, `end()`, the iterator categories (input, forward, bidirectional, random access).
- `<algorithm>` is the real power: `sort`, `find`, `count_if`, `transform`, `accumulate`, `copy`, `unique`, `lower_bound`, `all_of` — loops you never hand-write.
- `std::ranges` (C++20) pipelines: `views::filter(...)` | `views::transform(...)` — lazy, composable, no end() noise.
- **Erase-remove idiom:** `v.erase(std::remove(v.begin(), v.end(), x), v.end())` — or the C++20 `std::erase(v, x)`.

### 6. Lambdas & Functional
- `[capture](params) -> ret { body }` — captures by value `[=]`, by reference `[&]`, or explicitly `[x, &y]`; **dangling captures** (capturing by ref something that dies) are the classic bug.
- `std::function` — type-erased callable (has overhead); templates + concepts take any callable with zero cost.
- `std::bind` is legacy; lambdas replaced it.
- Algorithms + lambdas = the expressive core of modern C++: `std::sort(v.begin(), v.end(), [](a, b){ return a.size() < b.size(); })`.

### 7. Comparators & Hashing
- Ordering: strict weak ordering — `a < b` must be a consistent, transitive relationship or `std::sort` walks off the array (UB).
- `operator<` or a custom comparator for ordered containers; **`operator==` and `hash` must agree** for unordered containers (same contract as Java's `equals`/`hashCode`).
- `std::hash` specializations: `template<> struct std::hash<MyType> { size_t operator()(const MyType&) const; };`.
- Combining hashes: the standard trick `h ^= other_hash + 0x9e3779b9 + (h << 6) + (h >> 2)`.

### 8. Template Traits & SFINAE
- `std::is_integral<T>::value`, `std::enable_if`, type traits in `<type_traits>` — compile-time type interrogation.
- **SFINAE:** "Substitution Failure Is Not An Error" — an invalid template substitution just removes that overload from consideration, enabling tag dispatch and conditional APIs.
- The deliberate lesson: this is the *old* tool — concepts (topic 2) do the same job readably; you learn SFINAE to read the ecosystem's code.

---

# Module 05 — Modern C++

*Folder:* [`concepts/05-modern-cpp`](./concepts/05-modern-cpp) · ✅ Complete · **8 topics**

### 1. Move Semantics
- **lvalue** — has a name, addressable; **rvalue** — temporary, about to die. `T&&` binds to rvalues.
- **`std::move(x)`** casts to an rvalue: it *permits* the move constructor to steal x's guts (x is left valid-but-unspecified; don't read it).
- Move constructor `T(T&& other) noexcept` — cheap pointer steals instead of deep copies; `noexcept` matters or `vector` won't use it while growing.
- Copy = duplicate resources; move = transfer ownership. This is the performance feature C++11 added.

### 2. `auto` & Structured Bindings
- `auto` — inference for the lazy and the precise; `auto&` and `const auto&` in range-for to avoid copying.
- **Structured bindings (C++17):** `auto [key, value] = *map.begin();` and `for (auto& [k, v] : m)` — destructuring for pairs, tuples, and structs.
- `decltype(x)` for a variable's exact type.
- Rule: `auto` for obvious types, spelled types in public APIs.

### 3. `optional`, `variant`, `any`
- **`std::optional<T>`** — a value that may be absent: `std::optional<int> find(...)`; check `has_value()`, `value()`, `value_or(default)`. Replaces sentinel values and null returns.
- **`std::variant<A, B, C>`** — a type-safe union: holds one of the listed types; `std::visit` + lambdas dispatch on the active alternative (the pattern-matching switch).
- **`std::any`** — type-erased anything (last resort; `variant` is almost always better).
- Together: sum-type and option-type modeling — the functional tools that replace exception-driven control flow.

### 4. `constexpr` & Compile Time
- `constexpr` functions run **at compile time** when inputs are compile-time constants — the compiler computes, the binary stores the answer.
- `constexpr` variables, `if constexpr` (compile-time branch elimination — SFINAE's friendly replacement), `consteval` (must run at compile time).
- The payoff: constants computed once, lookup tables generated at build, zero runtime cost.

### 5. `string_view`, `span` & Ranges
- **`std::string_view`** — non-owning string slice (borrower beware); **`std::span<T>`** — non-owning view over a contiguous range (array, vector, C array).
- Both are pointer + length: free to pass, dangerous to store.
- **Ranges (C++20):** `views::iota`, `views::filter`, `views::transform`, `views::take` — composable, lazy pipelines with no begin/end noise.
- The mental model shift: views are recipes, not data — they execute as you iterate.

### 6. Error Handling
- **Exceptions** for exceptional failure — but heavy, invisible in the signature (vs Java's checked exceptions), and banned in many codebases.
- **Error codes / `std::expected<T, E>`-style patterns** — errors in the type, visible at the call site; this lab favors return-value error handling plus exceptions for truly exceptional paths.
- `noexcept` — a promise the function won't throw (move constructors should make it).
- **Assertions:** `assert` for invariants in debug; sanitizers catch what asserts miss.

### 7. Modern Class Features
- `[[nodiscard]]` — warn when the caller ignores the return value (an error code nobody checked).
- `= default` / `= delete` — control the special member functions explicitly.
- `inline` variables (C++17), nested namespaces `a::b::c`, designated initializers `Point{.x = 1, .y = 2}`.
- `explicit` constructors — stop implicit conversions from compiling.

### 8. `chrono`, Random & Filesystem
- **`std::chrono`:** `system_clock`, `steady_clock` (for measuring intervals — never `system_clock` for timing), `duration`, `time_point`, and the literals `100ms`, `1.5s`.
- **`<random>`:** `std::mt19937` (seeded, reproducible), `std::uniform_int_distribution` — never `rand()` (weak, biased).
- **`std::filesystem`:** `fs::path`, `exists`, `create_directories`, `directory_iterator`, `file_size` — the C++17 replacement for C's `dirent` and Python's `os`.

---

# Module 06 — Concurrency & Systems

*Folder:* [`concepts/06-concurrency-and-systems`](./concepts/06-concurrency-and-systems) · ✅ Complete · **7 topics**

### 1. Threads & `join`
- `std::thread t([]{ ... });` — a real OS thread; **`t.join()` before the `std::thread` dies** or the program terminates (`std::terminate`).
- **`std::jthread` (C++20)** — joins automatically in its destructor, and supports `stop_token` cooperative cancellation.
- Passing args to the thread function, and the reference-capture trap (dangling refs to locals).
- The shared-address-space model: threads see the same memory; Java is the same, but here it's fully explicit.

### 2. Mutexes & `lock_guard`
- `std::mutex` + **`std::lock_guard<std::mutex> lock(m);`** — RAII locking: unlocks on scope exit, even on exception (never `m.unlock()` by hand).
- `std::scoped_lock` (locks several mutexes, deadlock-free), `std::unique_lock` (deferred, timed, unlockable — needed with condition variables).
- The same race-condition lesson as Java: `count++` is read-modify-write, not atomic.

### 3. Atomics & Memory Order
- `std::atomic<int> x;` — `x.fetch_add(1)` and `x++` are atomic; also `load`, `store`, `compare_exchange_weak` (the CAS building block).
- **The memory-ordering model:** `memory_order_relaxed` (atomicity only), `acquire`/`release` (publish/consume pairing — a release-store pairs with an acquire-load), `seq_cst` (default, total order).
- `relaxed` for counters, `acquire/release` for flags guarding data, `seq_cst` when in doubt.
- This is the C++ equivalent of Java's `volatile`/`happens-before` lesson — but you can see the knobs.

### 4. Condition Variables & Producer-Consumer
- `std::condition_variable` + `unique_lock` — the wait/notify of C++: `cv.wait(lock, []{ return ready; })` (the predicate loop is built in — C++ solved Java's spurious-wakeup boilerplate).
- `notify_one` / `notify_all`; the classic lost-wakeup bug when notify happens before wait.
- The producer-consumer queue: mutex + condition variable + a bounded buffer — the canonical concurrent structure, same as Java Module 05's BlockingQueue.

### 5. Futures, Promises & `async`
- **`std::future<T>`** — a handle to a result that arrives later; `std::promise` is the writer side.
- `std::packaged_task` wraps a callable so its result (or its exception) lands in a future — the building block of the thread-pool project.
- `std::async(std::launch::async, f)` — runs f on a thread and returns a future; exceptions travel through futures.
- **The `future` destructor blocks** (for `async`-launched futures) — a quiet but important rule.

### 6. File I/O with `fstream`
- `std::ifstream` / `std::ofstream` / `std::fstream` — RAII files, close automatically.
- `open`, check `is_open()`, `getline(f, line)`, `<<` and `>>` (formatted), `.read()`/`.write()` (binary), `seekg`/`tellg` (random access).
- Errors as stream states (`fail()`, `bad()`, `eof()`) rather than exceptions (by default) — you must check them.
- Same lessons as Python's `with open` — but the destructor does the closing.

### 7. Loopback Sockets (POSIX)
- The raw C API under Java/Python sockets: `socket()` → `bind()` → `listen()` → `accept()` → `read`/`write` — on **127.0.0.1 only**.
- `sockaddr_in`, `htons` (endianness!), `AF_INET`/`SOCK_STREAM`, `close(fd)`.
- No classes, no exceptions — integers and return codes; C++ wraps this, the lab shows what's underneath.
- Everything binds or connects to loopback, by construction.

---

# Project 01 — Data Structures From Scratch

*Folder:* [`projects/project-01-data-structures-from-scratch`](./projects/project-01-data-structures-from-scratch) · ✅ Complete · **81 checks passing** · header-only C++20 templates, `make test` / `make sanitize`

Four classic structures with **no standard container inside them** — memory comes only from `std::allocator`, `new`, `delete`:

- **`dynamic_array.hpp`** — raw block from the allocator; capacity doubles when full; elements built with `construct_at` and moved with `move_if_noexcept`; `push_back` O(1) amortized, `insert`/`erase` O(n).
- **`linked_list.hpp`** — doubly-linked nodes; O(1) insert/erase with the node; O(n) indexed access.
- **`hash_map.hpp`** — separate chaining; rehashes at a load factor; chain lengths and rehash counts printed as measurements.
- **`min_heap.hpp`** — array-backed binary heap; sift up/down; the measured `heapify` vs repeated `add` comparison.

**The oracle method** (the C++ twin of Java's `14-dsa-in-java`): every structure is checked against the matching `std` container — `std::vector`, `std::list`, `std::unordered_map`, `std::priority_queue` — over thousands of seeded random operations (`std::mt19937`). A hand-rolled `CHECK` runner (no test framework) reports 81 passing checks, and `make test` also lints that the headers contain no std containers. Demos print measured, deterministic counts: copies, moves, rehashes, chain lengths, comparisons.

---

# Project 02 — Memory Safety Lab

*Folder:* [`projects/project-02-memory-safety-lab`](./projects/project-02-memory-safety-lab) · ✅ Complete · **50 checks passing** · toy bugs only, with the fix shown

### The method
Six deliberately buggy toy programs, each behind an explicit `--trigger` flag, built with `-std=c++20 -g -fsanitize=address,undefined`, run, and caught by the sanitizers — then each bug has a **fixed** counterpart. The lab's `RESULTS.md` records the real sanitizer output (pids and addresses normalized).

### The bug classes and what the sanitizer said

| Bug | What it is | Sanitizer headline |
|---|---|---|
| `use_after_free.cpp` | reading memory after `delete` | `AddressSanitizer: heap-use-after-free` |
| `heap_overflow.cpp` | writing past a heap allocation | `AddressSanitizer: heap-buffer-overflow` |
| `leak.cpp` | allocated, never freed | `LeakSanitizer: detected memory leaks` (120 bytes in 3 objects) |
| `double_free.cpp` | two `delete`s on one pointer | `AddressSanitizer: attempting double-free` |
| `stack_overflow_array.cpp` | indexing past a stack array (`int[4]`, index 4) | `AddressSanitizer: stack-buffer-overflow` + UBSan: `index 4 out of bounds for type 'int [4]'` |
| `uninitialized_read.cpp` | reading an uninitialized variable | **no report** — the honest lesson: sanitizers don't catch everything; `-Wuninitialized` and code review do |

### The lessons
- The sanitizer tells you **exactly what, where, and why** — file, line, allocation stack, free stack. Learning to read the report is the skill.
- Every fix is shown: RAII, smart pointers, bounds-checked access — the Module 02 toolkit applied.
- **Ethics:** toy programs in the author's own files, shown with the fix — defensive understanding, not exploit development.

---

# Project 03 — Thread Pool

*Folder:* [`projects/project-03-thread-pool`](./projects/project-03-thread-pool) · ✅ Complete · **28 checks passing** · built and measured on a 2-thread machine

### The design
A small, readable `ThreadPool` built on:
- **`std::jthread`** workers (auto-join, cooperative cancellation).
- A mutex-guarded task queue + **`std::condition_variable_any`** to wake sleeping workers.
- **`submit` returns a `std::future`** via `std::packaged_task` — results *and exceptions* travel back through the future.
- **Graceful shutdown:** queued tasks finish first (the destructor drains); `discard_pending` exists too, and it breaks the pending promises (so waiters see a broken-promise error, not a hang).

### What the tests prove (28 checks)
- Every task runs exactly once (5,000 tasks).
- Results come back in submission order through the futures; a single worker is FIFO.
- Exceptions propagate with their original type, and the pool survives them.
- Shutdown with pending tasks drains them; the destructor drains too.
- `discard_pending` breaks promises.
- No deadlock under 1,000 small tasks, four producer threads, nested submissions, and 200 quick create/destroy cycles.
- `ThreadPool(0)` still has a worker.

### The measured demo
Parallel word count over 2,000,000 generated in-memory words, sequential vs pooled — results must be identical, and the wall-clock timings print as labelled measurements alongside `std::thread::hardware_concurrency()` (= 2 on the build machine). The suite passed 30 of 30 consecutive runs; the deterministic lines were identical across runs, only the timing lines varied — stated plainly.

### Sanitizer status
Zero warnings with `-Wall -Wextra -Wpedantic -pthread`; clean under ASan+UBSan; one run under ThreadSanitizer with a documented, narrow suppression for a libstdc++ interaction — reported honestly in the README rather than hidden.

---

## How to Study These Notes

1. **Predict** the output and the memory state before running a snippet.
2. **Compile and run** the matching file: `g++ -std=c++20 -Wall -Wextra -Wpedantic -O0 -o demo file.cpp && ./demo` — then again with `-fsanitize=address,undefined`.
3. **Break it** — the module files and the memory-safety lab show how, and what the sanitizer says.
4. **Explain** who owns each byte, for how long, and who deletes it. If you can't, reread the section.
5. **Ship** — the repo's method: write, run, break, explain, ship.

*Consolidated from the completed files in this repository. Every claim here is checkable against the source files next to it.*
