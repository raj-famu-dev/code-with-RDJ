# 📘 java-by-RDJ — Complete Study Notes

> One consolidated reference covering every topic in this repository, with detailed explanations.
> Source: the completed concept folders (`01-basics` through `14-dsa-in-java`), plus `project-04-grade-manager`.
> Status key matches the folder READMEs: ✅ completed · ⬜ not started.

---

## 📑 Table of Contents

1. [Module 01 — Java Basics](#module-01--java-basics)
2. [Module 02 — Object-Oriented Programming](#module-02--object-oriented-programming)
3. [Module 03 — Collections Framework](#module-03--collections-framework)
4. [Module 04 — Exception Handling](#module-04--exception-handling)
5. [Module 05 — Multithreading & Concurrency](#module-05--multithreading--concurrency)
6. [Module 06 — Generics](#module-06--generics)
7. [Module 07 — File I/O (NIO.2)](#module-07--file-io-nio2)
8. [Module 08 — Lambdas & Streams](#module-08--lambdas--streams)
9. [Module 09 — Modern Java](#module-09--modern-java)
10. [Module 13 — Design Patterns & SOLID](#module-13--design-patterns--solid)
11. [Module 14 — Data Structures & Algorithms](#module-14--data-structures--algorithms)
12. [Project 04 — Grade Manager](#project-04--grade-manager)
13. [Pending Modules](#pending-modules)

---

# Module 01 — Java Basics

*Folder:* [`concepts/01-basics`](./concepts/01-basics) · ✅ Complete · **11 topics**

### 1. Hello World
Every Java program starts with a class containing a `main` method — the JVM's entry point.
```java
public class _1_HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
```
- `public class` — the class name must match the file name (`_1_HelloWorld.java`).
- `public static void main(String[] args)` — `public` so the JVM can call it, `static` so it runs without an object, `void` because it returns nothing.
- `System.out.println` prints to standard output and appends a newline.

### 2. Variables & Data Types
Java is **statically typed** — every variable's type is fixed at compile time.

| Category | Types | Size | Notes |
|---|---|---|---|
| Integer | `byte`, `short`, `int`, `long` | 1, 2, 4, 8 bytes | `int` is the default; `long` needs `L` suffix |
| Floating-point | `float`, `double` | 4, 8 bytes | `double` is the default; `float` needs `F` suffix |
| Character | `char` | 2 bytes | UTF-16 code unit, single quotes `'A'` |
| Boolean | `boolean` | JVM-dependent | only `true` / `false` |
| Reference | `String`, arrays, objects | — | points to an object on the heap |

- `var` (Java 10+) lets the compiler infer the type, but the variable is still statically typed.
- Literals: `1_000_000` (underscores for readability), `0b1010` (binary), `0xFF` (hex).

### 3. Operators
- **Arithmetic:** `+ - * / %` — integer division truncates (`7 / 2 == 3`).
- **Assignment:** `=`, `+=`, `-=`, `*=`, `/=`, `%=`.
- **Comparison:** `==`, `!=`, `<`, `>`, `<=`, `>=` — always yield `boolean`.
- **Logical:** `&&` and `||` **short-circuit** (right side may not run); `&` and `|` always evaluate both sides.
- **Bitwise:** `& | ^ ~ << >> >>>` — `>>>` is the unsigned right shift (fills with 0s).
- **Ternary:** `condition ? a : b` — an expression, unlike `if/else`.
- **Precedence matters:** `a + b * c`, `!x && y || z` — use parentheses when in doubt.

### 4. Type Casting
- **Widening (implicit, safe):** `int → long → float → double` — no data loss possible, compiler does it automatically.
- **Narrowing (explicit, lossy):** `double → int` requires a cast: `int x = (int) 3.99;` → `3` (truncates, no rounding).
- `char` ↔ `int` conversions use the Unicode code point.
- **Reference casting:** upcasting is automatic (`Dog` → `Animal`); downcasting needs `(Dog)` and fails at runtime with `ClassCastException` if the object isn't actually a `Dog`.
- Watch out for overflow: `(byte)(127 + 1)` wraps to `-128`.

### 5. Control Flow
- `if` / `else if` / `else` — the standard branching; conditions must be `boolean` (no truthiness like C).
- `switch` on `int`, `String`, `enum`, `char` — cases must be constants; `break` prevents fall-through (which is sometimes intentional).
- Modern switch expressions (Java 14+) use `->` and return values; covered in Module 09.

### 6. Loops
- `for` — when the count is known: `for (int i = 0; i < 10; i++)`.
- `while` — condition checked first; may run zero times.
- `do-while` — body runs at least once; condition checked after.
- `for-each` (`for (String s : list)`) — no index, no off-by-one, works on anything `Iterable` or an array.
- `break` exits the loop; `continue` skips to the next iteration; labeled breaks (`outer:`) escape nested loops.

### 7. Arrays
- Fixed-size, zero-based, stored contiguously; `new int[5]` gives all zeros.
- `arr.length` is a **field** (no parentheses), unlike `String.length()`.
- `Arrays.toString(arr)` for printing, `Arrays.sort(arr)`, `Arrays.fill(arr, val)`, `Arrays.copyOf(arr, newLen)`.
- **2D arrays:** `int[][] grid = new int[3][4];` — an array of arrays, so rows can have different lengths (jagged).
- **Common traps:** `ArrayIndexOutOfBoundsException` when indexing past `length - 1`; comparing arrays with `==` compares references — use `Arrays.equals`.

### 8. Strings
- `String` is **immutable** — every "modification" (`concat`, `replace`, `toUpperCase`) returns a new object. This enables string pooling and safe sharing across threads.
- The **string pool**: identical literals are reused (`"hi" == "hi"` is true for literals but false for `new String("hi")`). Always compare content with `.equals()`, never `==`.
- `+` on Strings is convenient but O(n) per concatenation in a loop — use `StringBuilder` (mutable, not thread-safe) or `StringBuffer` (synchronized).
- Useful methods: `charAt`, `substring`, `indexOf`, `contains`, `split`, `trim`, `strip`, `equalsIgnoreCase`, `length`, `isEmpty`, `isBlank`, `repeat`, `formatted`/`String.format`.
- `String.format("%s scored %.1f", name, grade)` — format specifiers like `%d`, `%f`, `%s`, `%n`.

### 9. Methods
- Signature = name + parameter types (return type is **not** part of it). Overloading requires different parameter lists.
- **Pass-by-value:** Java copies the *variable* — for primitives the value, for references the memory address. A method can mutate an object it receives but cannot reassign the caller's variable.
- `static` methods belong to the class (no `this`); instance methods need an object.
- `return` exits immediately; `void` methods may use bare `return;`.
- Varargs: `int sum(int... nums)` — `nums` is an array inside the method.

### 10. User Input
- `Scanner scanner = new Scanner(System.in);` — `nextInt()`, `nextLine()`, `nextDouble()`, `hasNextInt()`.
- The classic trap: `nextInt()` leaves the newline in the buffer, so a following `nextLine()` returns an empty string. Fix: call an extra `nextLine()` or read everything as lines and parse.
- `Scanner` should be closed (it closes `System.in`, so only close the last one).
- `Integer.parseInt(String)` converts text to a number and throws `NumberFormatException` on bad input (Module 04).

### 11. Output Formatting
- `System.out.println` / `print` / `printf` — `printf` uses format specifiers: `%d`, `%f` (with `%.2f` for decimals), `%s`, `%n`.
- `String.format` returns the formatted string instead of printing.
- Width and padding: `%10d` (right-align in 10), `%-10s` (left-align).
- `System.err` is the standard error stream.

---

# Module 02 — Object-Oriented Programming

*Folder:* [`concepts/02-oop`](./concepts/02-oop) · ✅ Complete · **15 topics**

### 1. Classes & Objects
- A **class** is a blueprint (fields + methods); an **object** is an instance created with `new` (allocated on the heap).
- State = fields, behavior = methods, identity = each `new` gives a distinct reference.
- `toString()` gives a human-readable representation; the default is `ClassName@hashcode`.

### 2. Constructors
- Same name as the class, no return type, runs on `new`.
- If you write none, Java provides a no-arg default; writing any constructor removes it.
- **Overloaded constructors** — `this(args)` chains to another constructor in the same class (must be the first statement).
- **Constructor chaining up the hierarchy:** every constructor calls `super()` implicitly first.

### 3. `this` Keyword
- Refers to the current object — disambiguates fields from parameters (`this.name = name`).
- `this(args)` delegates to another constructor; can't be combined with `super()` in the same constructor.
- Passing `this` to another method hands out a reference to the current object.

### 4. Encapsulation
- Fields `private`, exposure through public **getters/setters** that can validate: `setAge` can reject negatives.
- The object protects its own invariants — this is the point of encapsulation, not "adding getters".
- `this.name = name` inside the setter; validation logic lives in the setter, so every path through the code gets it.

### 5. Static vs Instance
- `static` members belong to the **class**, shared by all instances — one copy, not one per object.
- Static methods can't use `this` or instance fields directly; they're called as `ClassName.method()`.
- `static` counters are the standard way to count instances.
- The **order of initialization:** static initializers run once at class load, instance initializers + constructor run per object.

### 6. Inheritance
- `class Dog extends Animal` — Dog gets Animal's public/protected members. Java has **single inheritance** of classes (no multiple parent classes; interfaces fill that gap).
- `super.field` / `super.method()` reach the parent's version.
- **Every class implicitly extends `Object`** — hence `toString`, `equals`, `hashCode` exist everywhere.
- Prefer "is-a" for inheritance and "has-a" for composition (topic 13).

### 7. Polymorphism
- **Dynamic dispatch:** `Animal a = new Dog(); a.speak();` calls Dog's override — the runtime type decides, the compiler only checks that Animal has the method.
- Upcasting is automatic; downcasting needs a cast and a runtime check.
- **Method overriding rules:** same signature, covariant return type, can't reduce visibility, can't throw broader checked exceptions. Use `@Override` so the compiler catches typos.
- Overloading is compile-time (parameter lists); overriding is runtime (object type) — this is the key contrast.

### 8. Abstract Classes
- `abstract class` may mix concrete and `abstract` (unimplemented) methods; cannot be instantiated.
- A subclass must implement all abstract methods or itself be abstract.
- Abstract classes hold **state and shared code**; use when related classes share a common skeleton ("template method" style).
- Constructor still runs via `super()` during subclass construction.

### 9. Interfaces
- A **contract**: all methods implicitly `public abstract` (fields implicitly `public static final`).
- `implements` — a class can implement **many** interfaces (this is how Java does multiple inheritance of type).
- `default` methods (Java 8+) provide implementations in the interface itself.
- Choose an interface for capability (`Comparable`, `Runnable`), an abstract class for shared state and partial implementation.

### 10. Access Modifiers

| Modifier | Same class | Same package | Subclass (other pkg) | Everywhere |
|---|:-:|:-:|:-:|:-:|
| `private` | ✅ | ⬜ | ⬜ | ⬜ |
| *(package-private)* | ✅ | ✅ | ⬜ | ⬜ |
| `protected` | ✅ | ✅ | ✅ | ⬜ |
| `public` | ✅ | ✅ | ✅ | ✅ |

- Default practice: fields `private`, API `public`, internals package-private.

### 11. Enums
- A fixed set of named instances — `enum Day { MON, TUE, ... }` — type-safe constants (no typos, no magic ints).
- Can have fields, constructors (always private), and methods; each constant can override a method.
- Works with `switch`, has `values()`, `valueOf("MON")`, `ordinal()`.
- Great for states: `enum Status { ACTIVE, PAUSED, DONE }`.

### 12. `equals`, `hashCode`, `toString`
- **The contract:** if `a.equals(b)` is true then `a.hashCode() == b.hashCode()` — always. Breaking it breaks hash-based collections (HashMap, HashSet).
- `equals`: reflexive, symmetric, transitive, consistent, `x.equals(null)` is false.
- Override both together — `Objects.hash(...)` and `Objects.equals(...)` handle nulls safely.
- `toString` is called automatically in string concatenation and printing.

### 13. Composition
- **"Has-a"** (`Car` has an `Engine`) vs inheritance's **"is-a"** (`Dog` is an `Animal`).
- Composition is flexible: swap the engine at runtime, test with fakes, no fragile base class coupling.
- Rule of thumb: inherit only for true is-a; otherwise compose.

### 14. OOP Capstone
Combines classes, encapsulation, inheritance, polymorphism, interfaces, and enums into one working mini-program — the module's proof that the pieces work together.

### 15. Understanding the Basics of OOP
A reflection/summary file tying the four pillars together:
- **Encapsulation** — protect state behind methods.
- **Inheritance** — reuse and specialize.
- **Polymorphism** — one call, many behaviors.
- **Abstraction** — expose what matters, hide the rest.

---

# Module 03 — Collections Framework

*Folder:* [`concepts/03-collections`](./concepts/03-collections) · ✅ Complete · **13 topics**

### 1. Framework Overview
The two families:
- **`Collection`** (single items): `List` (ordered, duplicates), `Set` (unique), `Queue`/`Deque` (FIFO/LIFO/priority).
- **`Map`** (key→value pairs) — *not* a `Collection`.

### 2. ArrayList
- Backed by a **dynamic array**; O(1) `get`/`set` by index; O(n) insert/remove in the middle (shifting).
- Grows by ~1.5x when full, so `add` is amortized O(1) (see Module 14's measured 1.31 copies/add).
- Use for random access and append-heavy code.

### 3. LinkedList
- Doubly-linked nodes; O(1) insert/remove **if you already hold the node/iterator**, O(n) indexed access (must walk).
- Implements both `List` and `Deque` — stack and queue behavior for free.
- In practice `ArrayList` beats it for almost everything except heavy head/tail manipulation.

### 4. HashSet
- Unique elements, no order guarantees, backed by a hash table (a disguised HashMap of element→dummy).
- `add`, `contains`, `remove` are O(1) average — the fastest membership test.
- Requires proper `hashCode`/`equals` on the element type.

### 5. LinkedHashSet & TreeSet
- `LinkedHashSet` = HashSet + insertion-order doubly-linked list; slightly slower, iterates in insertion order.
- `TreeSet` = red-black tree; O(log n) operations, iterates **sorted**, and adds `first()`, `last()`, `floor()`, `ceiling()`, `headSet()`, `tailSet()` range queries.
- Requires `Comparable` elements or a supplied `Comparator`.

### 6. HashMap
- Key→value; keys unique; one `null` key allowed; O(1) average `get`/`put`.
- Buckets by `hash(key)`, resolves collisions by chaining; resizes when load factor > 0.75.
- Values can duplicate; **mutating a key after insertion breaks lookup** — use immutable keys.

### 7. HashMap Internals
- `hashCode()` → spread/`hash()` mixing → `index = hash & (table.length - 1)` (table length is a power of two so the mask works).
- Java 8+ turns long chains into red-black trees (bins ≥ 8), so worst case is O(log n), not O(n).
- Load factor and capacity: capacity × load factor triggers a resize with rehash of all entries.

### 8. LinkedHashMap & TreeMap
- `LinkedHashMap` preserves insertion order (or access order with access-order mode — the basis of simple LRU caches).
- `TreeMap` keeps keys **sorted**; O(log n); supports `firstKey`, `lastKey`, `subMap`, `headMap`, `tailMap`.
- `IdentityHashMap` compares by `==`; not covered in depth but part of the family.

### 9. Queue, Deque, PriorityQueue
- `Queue`: `offer`/`poll`/`peek` (return null on failure) vs `add`/`remove`/`element` (throw).
- `Deque` (double-ended): both stack (`push`/`pop`) and queue behavior — `ArrayDeque` is the recommended stack/queue in modern Java (not the legacy `Stack` class).
- `PriorityQueue`: a **binary heap** — `poll` returns the smallest per the comparator, not insertion order; O(log n) per op.

### 10. Iterators
- `Iterator` has `hasNext`, `next`, `remove` (the only safe way to remove during iteration).
- **`ConcurrentModificationException`:** modifying a collection with `list.remove(x)` while for-eaching it throws on the next `next()`. Use the iterator's `remove`, or `removeIf(pred)`.
- `ListIterator` adds bidirectional movement and `set`/`add`.

### 11. Comparable vs Comparator
- `Comparable` (`compareTo`) = **natural order**, built into the class — `"a".compareTo("b")`, `Integer`, `LocalDate`.
- `Comparator` = **external, flexible** ordering — multiple orders for the same type (by name, by price), passed to `sort` or `TreeMap`.
- Lambdas make comparators cheap: `list.sort(Comparator.comparing(Person::name).thenComparing(Person::age))`.

### 12. Utility & Immutable Collections
- `Collections.sort`, `reverse`, `shuffle`, `max`, `min`, `unmodifiableList`, `synchronizedList`, `emptyList`, `singletonList`.
- `List.of(...)`, `Map.of(...)` (Java 9+) — truly immutable; any mutation throws `UnsupportedOperationException`.
- `Arrays.asList` is fixed-size (a view of the array); `List.of` is fully immutable.

### 13. Collections Capstone
A combined exercise mixing the right structure for each job: set for uniqueness, map for lookup, priority queue for ordering, comparators for sorting.

---

# Module 04 — Exception Handling

*Folder:* [`concepts/04-exceptions`](./concepts/04-exceptions) · ✅ Complete · **8 topics** (code in `_1` written by RDJ)

### 1. Exception Handling Basics
- An exception is an object describing abnormal control flow; `try` guards it, `catch` handles it.
- Hierarchy: `Throwable` → `Error` (JVM-level, don't catch) and `Exception` → `RuntimeException`.
- Flow: when thrown, the stack unwinds until a matching `catch`; unmatched exceptions propagate to `main` and kill the JVM with a stack trace.
- Catch **specific** types first, general later — `catch (Exception e)` swallows everything (a debugging hazard).

### 2. Checked vs Unchecked
- **Checked** (`Exception` subclasses outside `RuntimeException`): the compiler forces `try/catch` or `throws` — e.g., `IOException`, `SQLException`. For conditions a caller can recover from.
- **Unchecked** (`RuntimeException`): compiler doesn't force handling — `NullPointerException`, `ArithmeticException`, `ArrayIndexOutOfBoundsException`, `IllegalArgumentException`. Usually bugs, not recoverable conditions.
- Design guidance: throw unchecked for programming errors, checked for recoverable conditions.

### 3. `throw` vs `throws`
- `throw new IllegalStateException("x")` **raises** an exception right now.
- `throws IOException` in a method signature **declares** that this method may let a checked exception escape — callers must deal with it.
- Stack traces are your friend: `e.getMessage()`, `e.printStackTrace()`, and the causing line number.

### 4. Custom Exceptions
- Extend `Exception` (checked) or `RuntimeException` (unchecked) to model domain errors: `InsufficientFundsException`, `InvalidGradeException`.
- Add fields and a constructor: `public InvalidGradeException(String detail) { super(detail); }`.
- Custom exceptions make error handling readable at the call site and self-documenting in the method signature.

### 5. Try-with-Resources
- `try (var in = new FileReader(path)) { ... }` — any `AutoCloseable` is closed **automatically**, in reverse order, even on exception.
- Strictly better than manual `finally` close: no leaked resources, no null checks before close, suppressed exceptions preserved.
- Multiple resources in one try; Java 9+ allows effectively-final variables.

### 6. Exception Chaining
- `catch (SQLException e) { throw new ServiceException("load failed", e); }` — pass the cause, don't lose it.
- The stack trace shows `Caused by:` sections, so the original root cause survives translation at each layer boundary.
- `initCause` / constructor `(message, cause)`; never swallow the cause — logging only the wrapper hides the bug.

### 7. `finally` Gotchas
- `finally` runs on success, on exception, and even on `return` in the try.
- **Gotchas:** `return` inside `finally` silently swallows the exception; a `finally` that throws replaces the original exception; `System.exit` skips finally.
- Since Java 7 prefer try-with-resources; use `finally` only for cleanup that isn't a resource.

### 8. Exceptions Capstone
A combined exercise: custom exceptions, propagation through layers, try-with-resources, and chaining in one small application.

---

# Module 05 — Multithreading & Concurrency

*Folder:* [`concepts/05-multithreading`](./concepts/05-multithreading) · ✅ Complete · **14 topics**

### 1. Thread Basics
- A thread is an independent call stack sharing the process's heap.
- `Thread t = new Thread(() -> ...); t.start();` — `start()` creates the new stack; calling `run()` directly runs it on the *current* thread (a classic bug).
- `Thread.sleep(ms)` pauses without releasing locks; `t.join()` waits for completion; `isAlive()`.

### 2. Runnable & Callable
- `Runnable.run()` returns nothing and can't throw checked exceptions — the simple "unit of work".
- `Callable.call()` returns a value and may throw — used with executors to get results back.
- Both are functional interfaces, so lambdas plug straight in.

### 3. Thread Lifecycle
States: `NEW` → `RUNNABLE` ↔ ( `BLOCKED` on a lock, `WAITING` on `wait()`/`join()`, `TIMED_WAITING` on `sleep(n)` ) → `TERMINATED`.
- Transitions are what matter: `wait` releases the lock and parks; `notify` wakes one waiter; a blocked thread needs the lock to proceed.

### 4. Race Conditions
- `count++` is three machine steps (read, add, write) — two threads can interleave and **lose an update**.
- Demonstrated in the repo by two threads incrementing a shared counter and printing a wrong total (timing-dependent output — the walkthrough says so).
- The fix is atomicity: `synchronized`, `AtomicLong`, or confinement to one thread.

### 5. `synchronized`
- A monitor lock per object: only one thread inside a `synchronized` method/block at a time.
- `synchronized(this)` vs a private `final Object lock` — the latter prevents outsiders from locking your monitor.
- Guarantees **mutual exclusion** and **memory visibility** (flushes CPU caches).
- Cost: threads queue up; coarse locking kills parallelism.

### 6. `volatile` & the Memory Model
- The Java Memory Model: each thread may cache fields; without synchronization, writes by one thread may never be seen by another.
- `volatile` guarantees visibility and ordering for that field (reads/writes go to main memory), and prevents instruction reordering.
- **`volatile` is not atomicity:** `volatile count++` still races (check-then-act). Use it for flags (`stop = true`), use `Atomic*` or locks for read-modify-write.
- `happens-before` links: unlock of a lock happens-before the next lock of the same monitor.

### 7. `wait` / `notify`
- The producer-consumer primitive: `wait()` releases the lock and sleeps until `notify()`/`notifyAll()`.
- Must be called **inside** `synchronized` on the same object, or `IllegalMonitorStateException` is thrown.
- Standard pattern: `while (queue.isEmpty()) wait();` — a loop, not an `if`, because of **spurious wakeups** and re-checking after `notifyAll`.
- `notifyAll` (wake everyone, losers re-check) is safer than `notify` (one random winner, possible missed signals).

### 8. ExecutorService
- Don't hand-manage threads — submit `Runnable`/`Callable` to a pool: `Executors.newFixedThreadPool(n)`.
- `submit` returns a `Future`; `shutdown()` stops accepting tasks, `shutdownNow()` interrupts running ones, `awaitTermination` waits.
- Pool types: fixed, cached (grows on demand), single-thread (order guarantee), `newVirtualThreadPerTaskExecutor` (see topic 13).
- Always shut the executor down, ideally with try-with-resources (it's `AutoCloseable` in modern Java).

### 9. Future & CompletableFuture
- `Future.get()` **blocks** until the result is ready (or timeout); `isDone`, `cancel`.
- `CompletableFuture` adds composition: `thenApply`, `thenCompose` (chaining), `thenCombine` (joining two), `exceptionally`/`handle` (recovery).
- Enables non-blocking pipelines: fetch → transform → combine, all without waiting at each step.

### 10. Locks & Atomics
- `ReentrantLock`: explicit `lock()`/`unlock()` in a `try/finally`, supports `tryLock()` (non-blocking), fairness, and multiple conditions (`await`/`signal` — the `wait/notify` upgrade).
- `ReadWriteLock` (`ReentrantReadWriteLock`): many concurrent readers, one writer.
- `AtomicInteger`, `AtomicLong`, `AtomicReference`: lock-free CAS loops — `incrementAndGet()`, `compareAndSet()`. Fast for simple counters and flags.

### 11. Concurrent Collections
- `ConcurrentHashMap`: lock-striping — threads rarely block each other; `compute`, `merge`, `putIfAbsent` are atomic compound actions.
- `CopyOnWriteArrayList`: every write copies the array — great for read-heavy/iterate-while-modify, terrible for write-heavy.
- `BlockingQueue` (`ArrayBlockingQueue`, `LinkedBlockingQueue`): `put` blocks when full, `take` blocks when empty — producer/consumer without manual wait/notify.

### 12. Deadlock
- Thread A holds lock 1 wants lock 2; thread B holds lock 2 wants lock 1 — both wait forever.
- Conditions (Coffman): mutual exclusion, hold-and-wait, no preemption, circular wait. **Break circular wait**: always acquire locks in a fixed global order.
- Also covered: livelock (threads keep reacting, no progress) and starvation (a thread never gets the lock).
- Diagnose with a thread dump (`jstack`) — the dump shows "waiting to lock" cycles.

### 13. Virtual Threads (Java 21)
- Platform threads = OS threads (expensive, ~MB stacks, thousands at best). Virtual threads are JVM-managed (tiny, stack grows on demand) — **millions** are cheap.
- Best for **blocking I/O** (HTTP calls, DB queries), not CPU-bound loops.
- `Thread.ofVirtual().start(...)` or `Executors.newVirtualThreadPerTaskExecutor()`.
- The repo measures the same blocking tasks on platform vs virtual threads — virtual threads finish dramatically faster when tasks block.
- Rule: virtual threads don't make a single task faster; they make *many blocking tasks* cheap.

### 14. Concurrency Capstone
A combined exercise: a thread pool, a shared concurrent structure, safe publication, and measured speedup — proving the pieces work together.

---

# Module 06 — Generics

*Folder:* [`concepts/06-generics`](./concepts/06-generics) · ✅ Complete · **6 topics**

### 1. Generic Classes
- `class Box<T> { private T value; }` — type parameter filled at use: `Box<String>`.
- Compile-time type safety: no casts, no `ClassCastException` from heterogeneous collections.
- Convention: `T` type, `E` element, `K`/`V` key/value, `R` return.

### 2. Generic Methods
- `<T> T first(List<T> list)` — the type parameter declared before the return type; inferred at the call site.
- Generic methods can be on non-generic classes; often static utilities (`Collections.swap`).

### 3. Bounded Types
- `<T extends Comparable<T>>` — constrains T to a type with the needed behavior; the compiler then lets you call `compareTo` on T.
- Multiple bounds: `<T extends Animal & Serializable>` — class first, interfaces after.

### 4. Wildcards
- `List<? extends Number>` — **producer** (read Numbers out; can't add — except null).
- `List<? super Integer>` — **consumer** (write Integers in; reading gives `Object`).
- Mnemonic: **PECS — Producer Extends, Consumer Super** (from *Effective Java*).
- Unbounded `List<?>` — unknown type, only `Object` operations.

### 5. Type Erasure
- Generics exist only at compile time; the runtime has just `Object` (plus the bounds' type).
- Consequences: `List<String>.class == List<Integer>.class` (one class), no `new T()`, no `T[]` generic arrays, no `instanceof List<String>`.
- Bridges the gap with legacy pre-Java-5 code via raw types.

### 6. Generics Capstone
A generic container/API exercise combining bounds, wildcards, and methods — e.g., a type-safe repository or event bus.

---

# Module 07 — File I/O (NIO.2)

*Folder:* [`concepts/07-file-io`](./concepts/07-file-io) · ✅ Complete · **7 topics**

### 1. Path & Files
- `Path` is an abstract path; `Paths.get("a", "b", "c.txt")`; `Files` operates on it.
- Key calls: `Files.exists`, `createDirectories`, `size`, `isDirectory`, `delete`, `copy`, `move`, `walk` (streams a directory tree).
- NIO.2 replaced the legacy `File` class — better error messages, more operations.

### 2. Reading Text Files
- `Files.readString(path)` — whole file to a String (small files).
- `Files.readAllLines(path)` → `List<String>`.
- `Files.lines(path)` → `Stream<String>` — lazy, memory-friendly for big files (must be closed — try-with-resources).
- `BufferedReader` for line-by-line control; `Scanner` for parsing tokens.

### 3. Writing Text Files
- `Files.writeString(path, content)` — replaces or creates (`StandardOpenOption.APPEND` to append).
- `Files.write(path, lines)`.
- `BufferedWriter` for many writes (flushing matters).
- `Files.newBufferedWriter` with options: `CREATE`, `APPEND`, `TRUNCATE_EXISTING`.

### 4. Binary I/O
- Byte streams (`InputStream`/`OutputStream`) vs character streams (`Reader`/`Writer`).
- `BufferedInputStream` / `BufferedOutputStream` wrap raw streams for performance.
- Reading a file into `byte[]`: `Files.readAllBytes`; copying: `Files.copy(in, out)`.
- `DataOutputStream`/`DataInputStream` write primitives in a defined format.

### 5. CSV & JSON
- CSV: `String.split(",")` with a regex handling quoted fields; simple, no dependency.
- JSON: Java has no built-in JSON — libraries like Jackson/Gson do `readValue`/`writeValue` between JSON text and objects.
- Manual parsing teaches why libraries exist (escaping, nesting, types).

### 6. Serialization & Its Dangers
- `implements Serializable` + `ObjectOutputStream.writeObject` → bytes; `readObject` restores.
- `serialVersionUID` — versioning; mismatch throws `InvalidClassException`.
- **The dangers:** class changes break compatibility; security (deserializing untrusted data = remote code execution risk); size and speed.
- `transient` fields skip serialization. Modern practice: prefer JSON.

### 7. File I/O Capstone
Combined exercise: safe read-transform-write with validation, error handling, and atomic-ish writes.

---

# Module 08 — Lambdas & Streams

*Folder:* [`concepts/08-lambdas-streams`](./concepts/08-lambdas-streams) · ✅ Complete · **8 topics**

### 1. Functional Interfaces
- An interface with exactly one abstract method — the target of lambdas.
- The `java.util.function` toolbox: `Function<T,R>` (`apply`), `Predicate<T>` (`test`), `Consumer<T>` (`accept`), `Supplier<T>` (`get`), `BiFunction`, `UnaryOperator`.
- Lambdas implement these directly: `Predicate<String> isEmpty = s -> s.isEmpty();`.

### 2. Lambdas & Method References
- Lambda = anonymous function: `(a, b) -> a + b`. Types inferred from the target.
- Captures local variables only if **effectively final** (not reassigned).
- Method references are shorter lambdas: `String::toUpperCase`, `System.out::println`, `this::helper`, `ArrayList::new`.

### 3. Stream Basics
- A pipeline: **source → intermediate ops → terminal op**.
- Streams are **lazy** and **single-use** — intermediate ops do nothing until a terminal op (`collect`, `forEach`, `count`, `anyMatch`) pulls data through.
- `list.stream()` creates; unlike collections, streams don't store data.

### 4. map, filter, reduce
- `filter(p)` keeps matching elements; `map(f)` transforms each; `reduce` collapses to one value (`reduce(0, Integer::sum)`).
- `mapToInt`/`mapToDouble` give numeric streams with `sum()`, `average()`, `max()`.
- `sorted`, `distinct`, `limit`, `skip`, `flatMap` (one-to-many flattening — e.g., words of many sentences).

### 5. Collectors
- `collect(Collectors.toList())`, `toSet()`, `toMap(keyFn, valFn)`.
- `Collectors.groupingBy(classifier)` → `Map<K, List<V>>`; `partitioningBy(predicate)` → true/false groups.
- `joining(", ")`, `counting()`, `summingInt`, `averagingDouble`.
- `collect(Collectors.groupingBy(Person::city, Collectors.counting()))` replaces whole loops.

### 6. Lazy Evaluation
- Intermediate operations build a recipe; nothing runs until the terminal operation, and elements flow **one at a time** (short-circuit ops like `findFirst` may examine only the first element).
- `anyMatch`, `findAny`, `takeWhile`, `dropWhile` short-circuit.
- Infinite streams work because of laziness: `Stream.iterate(1, n -> n * 2).limit(10)`.
- Two runs of one terminal op? Can't — streams are single-use (throws `IllegalStateException`).

### 7. Optional Done Right
- `Optional<T>` = a container that may hold a value — replaces `null` returns.
- `map`, `filter`, `flatMap` chain without unwrapping: `opt.map(String::trim).filter(s -> !s.isEmpty())`.
- `orElse(default)`, `orElseGet(() -> expensive())` (lazy), `orElseThrow()`.
- **Done right:** return Optional for "may be absent", never `Optional` fields/parameters, never `get()` without `isPresent` (or use the chaining API), don't use `isPresent()+get()` if a chain works.

### 8. Streams Capstone
Combined exercise: a data pipeline with filter → map → sorted → grouped collection over realistic data.

---

# Module 09 — Modern Java

*Folder:* [`concepts/09-modern-java`](./concepts/09-modern-java) · ✅ Complete · **7 topics**

### 1. `var` & Text Blocks
- `var` — local variable type inference: `var list = new ArrayList<String>();`. Compile-time only, still statically typed; can't use on fields or parameters.
- Text blocks (Java 15): multi-line strings with real newlines; `"""` fences; incidental indentation stripped based on the closing fence; `\` line continuation and `\n` escape.

### 2. Records
- `record Point(int x, int y) {}` — a transparent carrier of immutable data.
- Auto-generated: canonical constructor, `x()`/`y()` accessors, `equals`, `hashCode`, `toString`.
- Compact constructors for validation: `Point { if (x < 0) throw ...; }`.
- Ideal DTOs — no boilerplate; the "right kind" of immutability (vs Lombok-style classes).

### 3. Sealed Classes
- `sealed interface Shape permits Circle, Square, Triangle {}` — **exhaustive** hierarchies known at compile time.
- Enables exhaustive `switch` without a default arm: if you add a `Shape`, the compiler flags every non-exhaustive switch.
- Subclasses must be `final`, `sealed`, or `record`. Domain modeling: closed sets of variants.

### 4. Switch Expressions & Patterns
- Switch **expressions** return values: `int days = switch (d) { case MON, TUE -> 1; ... };`
- `->` labels: no fall-through, no `break` needed; `yield` for block bodies.
- **Pattern matching for switch** (Java 21): `case Circle c -> ...`, with `when` guards (`case Circle c when c.radius() > 10 ->`).
- Combined with sealed types: type-safe variant handling — the sum-type workflow.

### 5. java.time API
- Replaced the terrible `Date`/`Calendar`. Core types: `LocalDate` (no time), `LocalTime`, `LocalDateTime`, `ZonedDateTime` (with zone), `Instant` (UTC machine time), `Duration` (time-based), `Period` (date-based).
- Immutable — every operation returns a new object: `date.plusDays(3)`, `d.isBefore(other)`, `between(a, b)`.
- Parsing/formatting: `LocalDate.parse("2026-11-03")`, `DateTimeFormatter`.
- Human-friendly: `date.withDayOfMonth(1)`, `date.datesUntil(other)`.

### 6. HttpClient
- The modern (`java.net.http`, Java 11+) HTTP client — replaces `HttpURLConnection`.
- `HttpClient client = HttpClient.newHttpClient();` then `HttpRequest` (builder: URI, header, method, `BodyPublishers.ofString`) and `client.send(request, BodyHandlers.ofString())` → `HttpResponse` (statusCode, body).
- Supports async (`sendAsync` → `CompletableFuture<HttpResponse>`), HTTP/2, and timeouts.
- Checked `IOException`/`InterruptedException` — try-with-resources not needed (client is cheap and reusable).

### 7. Modern Java Capstone
Combined exercise: records + sealed types + pattern-matching switch + java.time + HttpClient in one small program.

---

# Module 13 — Design Patterns & SOLID

*Folder:* [`concepts/13-design-patterns`](./concepts/13-design-patterns) · ✅ Complete · **10 topics**

### 1. SOLID Principles
- **S — Single Responsibility:** one reason to change per class.
- **O — Open/Closed:** open for extension, closed for modification (strategy/plugin beats editing a `switch`).
- **L — Liskov Substitution:** subtypes must be usable wherever the parent is, without surprises.
- **I — Interface Segregation:** small, focused interfaces (`Printable`, `Scannable`) vs one fat `Machine`.
- **D — Dependency Inversion:** depend on abstractions (`interface PaymentProcessor`), not concretions.

### 2. Singleton
- Exactly one instance, global access point: private constructor + static `getInstance()`.
- The thread-safe modern form: **enum singleton** or holder idiom; `synchronized getInstance()` is correct but slow.
- Honest framing in the repo: it's global mutable state in disguise — use sparingly.

### 3. Factory
- A method creates objects so callers don't `new` concrete types: `AnimalFactory.create("dog")`.
- Decouples creation from use; centralizes the "which class?" decision.
- Simple factory (covered) vs Factory Method (subclass decides) vs Abstract Factory (families of products).

### 4. Builder
- Telescoping constructors (`new Person(a, b, c, d, e)`) become readable construction: `Person.builder().name("Raj").age(20).build()`.
- Handles optional parameters, immutable targets, and validation at `build()`.
- `StringBuilder` is the classic in-JDK example; records can carry a `Builder`.

### 5. Adapter
- Converts one interface into another the client expects: `LegacyPrinter` wrapped so it satisfies the new `Printer` interface.
- Use when integrating mismatched systems — the glue pattern. Composition (wrapping the adaptee) beats multiple inheritance.

### 6. Decorator
- Wraps an object to add behavior without subclassing: `new LoggingNotifier(new EmailNotifier(new BaseNotifier()))`.
- Each layer implements the same interface and delegates inward — stackable, runtime-composable.
- `java.io` is decorators all the way down (`new BufferedReader(new InputStreamReader(System.in))`).

### 7. Strategy
- Encapsulate interchangeable algorithms: `interface SortStrategy`, injected at runtime.
- Replaces conditional (`if type == ...`) algorithm selection with polymorphism — the go-to Open/Closed fix.
- Lambdas make single-method strategies trivial: `list.sort(comparator)` *is* strategy injection.

### 8. Observer
- One-to-many notification: `Subject` keeps a list of `Observer`s, `notifyAll()` on change; observers subscribe/unsubscribe.
- Loose coupling — the subject knows only the interface. The backbone of event systems, GUIs, and pub/sub.
- Watch for: memory leaks from un-removed observers, listener ordering, exception in one observer affecting others.

### 9. Command
- Encapsulate a request as an object: `interface Command { void execute(); }` — stores the *what*, decoupled from the *when/who*.
- Enables undo stacks, queues, macros, logging of operations.
- Lambdas are lightweight commands; full objects carry state (parameters, undo info).

### 10. Refactor: Bank System
The capstone — a procedural/conditional version of a small bank system refactored to Strategy (interest calculation), Observer (transaction notifications), and SOLID (interfaces, dependency inversion, single responsibility), showing before/after and why each change helps.

---

# Module 14 — Data Structures & Algorithms

*Folder:* [`concepts/14-dsa-in-java`](./concepts/14-dsa-in-java) · ✅ Structures complete (algorithms ⬜) · **8 structures, each built from scratch and checked against the JDK on seeded random operations**

### Big-O recap
| Structure | Access | Search | Insert | Delete | Notes |
|---|---|---|---|---|---|
| Dynamic array | O(1) index | O(n) | O(1)* end / O(n) middle | O(n) | *amortized |
| Linked list | O(n) | O(n) | O(1) with node | O(1) with node | doubly-linked here |
| Stack / Queue | O(n) top-only | O(n) | O(1) | O(1) | LIFO / FIFO |
| Hash map | — | O(1)* key | O(1)* | O(1)* | *average, good hash |
| BST | O(log n)* | O(log n)* | O(log n)* | O(log n)* | *only if balanced |
| Min-heap | O(1) min | O(n) | O(log n) | O(log n) | root = smallest |
| Graph (adj. list) | — | O(V+E) | O(1) edge add | O(E) | BFS/DFS below |
| Trie | — | O(L) | O(L) | O(L) | L = word length |

### 1. Dynamic Array
- What `ArrayList` is inside: an `Object[]` plus a size, doubling capacity when full.
- Measured in the repo: **1.31 copies per add** over 100,000 adds with 15 resizes — doubling makes `add` amortized O(1).
- `insert`/`remove` in the middle shift elements — O(n).

### 2. Linked List
- Nodes (`data`, `prev`, `next`) linked in both directions; head and tail tracked.
- O(1) insertion/removal **at the ends** and when you hold the node; O(n) indexed access.
- Trade-off vs arrays: no resize, no shifting, but pointer memory and poor cache locality.

### 3. Stack & Queue
- **Stack (LIFO):** `push`, `pop`, `peek`, all O(1) — call stacks, undo, expression evaluation, DFS.
- **Queue (FIFO):** `offer`, `poll`, `peek` — scheduling, BFS, buffering.
- Implemented on the linked list (both ends O(1)).

### 4. HashMap with Chaining
- `hashCode → index` into buckets; collisions stored as lists in the bucket; resize when load factor exceeded.
- **Measured in the repo:** a constant `hashCode()` puts all 500 keys in one bucket — a hash map silently degrades to a linked list. Good hash = spread.
- O(1) average `get`/`put`/`remove` with a good hash; O(n) worst case.

### 5. Binary Search Tree
- Left < node < right; `contains`/`insert`/`delete` follow one path — O(h).
- **Measured in the repo:** sorted insertion gives height 1000 (a linked list), shuffled gives height ~24 for 1,000 keys — balance is everything; self-balancing variants (AVL, red-black — what `TreeMap` uses) fix this.
- In-order traversal yields sorted order.

### 6. Min-Heap
- Complete binary tree in an array (children at `2i+1`, `2i+2`), parent ≤ children; root is the minimum.
- `add` bubbles up, `remove`/`heapify` sifts down — O(log n).
- **Measured in the repo:** heapify (74,453 swaps) beats repeated `add` (128,055 swaps) on 100,000 values.
- Powers `PriorityQueue` and heapsort.

### 7. Graph (BFS & DFS)
- Adjacency list (`Map<Node, List<Edge>>`); BFS uses a **queue** (level order, shortest path in unweighted graphs); DFS uses a **stack**/recursion (path finding, cycle detection, backtracking).
- Both O(V+E); visited-set prevents infinite loops on cycles.
- BFS finds shortest edge-count path; DFS finds *a* path and explores deep.

### 8. Trie
- Character-per-level tree for prefix lookups; a node = children map + end-of-word flag.
- `insert`/`contains`/`startsWith` all O(word length) — independent of dictionary size.
- Powers autocomplete, spell-check, IP routing. Space cost: many nodes.

### Algorithms (⬜ not started)
The planned algorithms list and a personal problem log are still open per the folder README.

---

# Project 04 — Grade Manager

*Folder:* [`projects/project-04-grade-manager`](./projects/project-04-grade-manager) · ✅ Complete · the capstone for `01-basics`

A console application written, tested and debugged by RDJ himself (no AI assistance), combining everything from Module 01:
- **Methods & control flow** — menu loop with `switch`/`if` branching.
- **Arrays/ArrayLists** — storing students and grades.
- **User input with `Scanner`** — including the newline-buffer trap handling.
- **Input validation** — rejecting invalid grades with loops/conditionals.
- **String formatting** — aligned output tables with `printf`.
- **Separation of concerns** — grade calculation logic split from presentation, foreshadowing OOP.

---

# Pending Modules

These exist in the plan but are ⬜ **not started** (they need a database, build tools or Docker on a local machine, per the folder README):

| Module | Focus |
|---|---|
| `10-jdbc-sql` | SQL, JDBC, transactions, DAO pattern |
| `11-testing` | JUnit 5, Mockito, TDD, coverage |
| `12-build-tools` | Maven and Gradle |
| `15-spring-boot` | REST, JPA, security, testing, Docker |

Projects 01–03, 05–08 (calculator, todo app, bank system, contact book, concurrent file processor, Spring Boot task API, LLM client service) are also planned but not started.

---

## How to Study These Notes

1. **Predict** the output of a snippet before running it.
2. **Run** the matching file in the concept folder (`javac` + `java`, JDK 21).
3. **Break** it on purpose (the files end with trap ideas) and explain the error.
4. **Explain** the topic out loud in plain English — if you can't, reread the section.
5. **Ship**: the repo's own method — write, run, break, explain, ship.

*Consolidated from the completed files in this repository. Every claim here is checkable against the source files next to it.*
