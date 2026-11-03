# `_6_AbstractClassesAndInterfaces.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
An abstract class has at least one pure virtual function (`virtual ... = 0;`). You cannot create an object of it; derived classes must override every pure virtual before they can be instantiated. C++ has no `interface` keyword: an "interface" is just an abstract class with no data, only pure virtual functions and a virtual destructor.

This is how C++ expresses "any type that can do X", and it is the tool behind plugin systems and swappable back-ends.

## Full Line-by-Line Breakdown

### SECTION 1: interface-style class
`IPrintable` has one pure virtual function and a virtual destructor. `std::is_abstract_v<T>` is a compile-time check that confirms it is abstract; the file cannot actually write `IPrintable p;` because that would be a compile error. `IComparableById` adds a normal (non-virtual) helper `sameIdAs` that uses the pure `id()`: C++ interface-style classes may carry shared implementation, similar to a Java `default` method.

Output from a real run:

```text
===== SECTION 1: interface-style class =====
is_abstract<IPrintable>: true
`IPrintable p;` would not compile: cannot instantiate an abstract class.
is_polymorphic<IPrintable>: true
```

### SECTION 2: abstract class with state
`Employee` implements both interfaces (multiple inheritance is normal here), stores shared data (`id_`, `name_`) and declares its own pure virtual `pay()`. `Salaried` and `Hourly` override `pay`, so they are concrete. `Incomplete` forgets, and `is_abstract_v<Incomplete>` is true; instantiating it would not compile. The vector holds `unique_ptr<Employee>`, so objects are not sliced and are deleted correctly thanks to the virtual destructors in the interfaces. Through an `IPrintable&` you only see `print()`: code depends on the interface, not the class.

Output from a real run:

```text
===== SECTION 2: abstract class with state =====
is_abstract<Employee>: true
is_abstract<Salaried>: false
is_abstract<Incomplete>: true (forgot to override pay(), so still abstract; `Incomplete x;` would not compile)
  Employee#1 Ana pays 10000
  Employee#2 Ben pays 1600
sameIdAs: false (ids 1 vs 2)
via IPrintable& only: Employee#2 Ben pays 1600
```

### SECTION 3: pure virtual with a body
A pure virtual function may still have a definition outside the class. Derived classes must override it, but may call it explicitly (`Logger::log(...)`) to reuse default behavior. Rare, but it appears in real code, for example to make a destructor pure while still providing a body.

Output from a real run:

```text
===== SECTION 3: pure virtual with a body =====
  [default log] console says: hello
A pure virtual may still have a definition; derived classes must override it but may call it explicitly.
```

### SECTION 4: the memory cost of interfaces
An interface with no data still has a hidden vptr (8 bytes here). `Employee` inherits two polymorphic bases, so it has two vptrs, plus its own data (these sizes are for x86-64 g++ 13). Multiple interfaces therefore cost a pointer each per object.

Output from a real run:

```text
===== SECTION 4: the memory cost of interfaces =====
sizeof(IPrintable) = 8 (only the hidden vptr; no data)
sizeof(Employee) = 56 (two vptrs for two bases + data)
Employee has two vptrs because it inherits from two polymorphic bases (multiple inheritance).
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `interface Printable { String print(); }` | `class IPrintable { public: virtual ~IPrintable() = default; virtual std::string print() const = 0; };` |
| `implements A, B` | `class X : public A, public B` |
| `abstract class` keyword | Any class with a `= 0` function is abstract |
| Interface methods are public automatically | You write `public:` yourself |
| Interfaces cannot hold fields | An interface-style class could hold fields; convention keeps them out |
| Default methods | Ordinary non-virtual or virtual members with bodies |
| Multiple class inheritance forbidden | Multiple inheritance of implementation allowed (use sparingly; diamond problem exists) |

## Key Rules / Gotchas Recap
- Give every interface-style class a `virtual ~T() = default;`.
- All pure virtuals must be overridden or the derived class stays abstract.
- Use `override` on implementations to catch signature mismatches.
- Store polymorphic objects through `unique_ptr`/references, never by value.
- Each polymorphic base adds a vptr to the object.

## Why This Structure Exists
Swapping implementations behind a stable interface (an inference engine on CPU vs GPU, a scanner that checks different vulnerability classes, a storage back-end) keeps the rest of the program independent of the details, which also makes it testable.
