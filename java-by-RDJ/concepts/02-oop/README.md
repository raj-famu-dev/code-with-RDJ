# 📘 02 — Object-Oriented Programming (OOP)

> The four pillars — Encapsulation, Inheritance, Polymorphism, Abstraction — and everything that supports them. This is where Java stops being just syntax and starts being a way of modeling real systems.

![Language](https://img.shields.io/badge/Language-Java%2021-orange)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Type](https://img.shields.io/badge/Type-Concept%20Practice-blue)

---

## 📌 About This Folder

Each file here is a **standalone, runnable program** isolating exactly one core OOP concept, building directly on everything learned in `01-basics`. Every program is documented below with the concept it teaches, why that concept matters, its syntax pattern, and the gotchas that trip people up.

This README serves two purposes:
1. **My own reference** — a fast lookup for syntax I've already learned.
2. **A portfolio artifact** — proof of what I understand and can build with, for anyone reviewing this repo.

---

## ✅ Progress Tracker

| # | File | Concept | Status |
|---|------|---------|:---:|
| 1 | [`_1_ClassesAndObjects.java`](./_1_ClassesAndObjects.java) | Classes as blueprints, objects as instances | ✅ |
| 2 | [`_2_Constructors.java`](./_2_Constructors.java) | Default, parameterized, overloaded constructors | ✅ |
| 3 | [`_3_ThisKeyword.java`](./_3_ThisKeyword.java) | Self-reference, chaining, method returns | ✅ |
| 4 | [`_4_Encapsulation.java`](./_4_Encapsulation.java) | Private fields, getters/setters, validation | ✅ |
| 5 | [`_5_StaticVsInstance.java`](./_5_StaticVsInstance.java) | Static vs instance members | ✅ |
| 6 | [`_6_Inheritance.java`](./_6_Inheritance.java) | extends, super, method overriding | ✅ |
| 7 | [`_7_Polymorphism.java`](./_7_Polymorphism.java) | Runtime polymorphism, dynamic dispatch | ✅ |
| 8 | [`_8_AbstractClasses.java`](./_8_AbstractClasses.java) | Abstract classes and methods | ✅ |
| 9 | [`_9_Interfaces.java`](./_9_Interfaces.java) | implements, default/static interface methods | ✅ |
| 10 | [`_10_AccessModifiers.java`](./_10_AccessModifiers.java) | public/private/protected/default | ✅ |
| 11 | [`_11_Enums.java`](./_11_Enums.java) | Fixed constant sets, enums with fields/methods | ✅ |
| 12 | [`_12_EqualsHashCodeToString.java`](./_12_EqualsHashCodeToString.java) | Overriding equals(), hashCode(), toString() | ✅ |
| 13 | [`_13_Composition.java`](./_13_Composition.java) | Has-a relationships vs inheritance | ✅ |
| 14 | [`_14_OOPCapstone.java`](./_14_OOPCapstone.java) | All 4 pillars combined in one design | ✅ |

**`02-oop` is complete — all 14 topics, from first object to a full capstone design.**

---

## 🗂 Concept Log

### 1️⃣ `_1_ClassesAndObjects.java`
**Concept:** Classes as blueprints, objects as actual instances created from them

**Why it matters:** This is the fundamental mental shift from `01-basics` — everything before this was primitives and static procedural code. OOP starts here: a class describes shape, an object is the real thing built from it, and every later OOP concept assumes you already think this way.

**Syntax formula:**
```java
class Car {
    String brand;
    void startEngine() { }
}

Car car1 = new Car();
car1.brand = "Toyota";
car1.startEngine();
```

**Key rules / gotchas:**
- Nothing exists in memory until `new` is called — the class alone is just a description
- Each object has its own independent copies of fields; changing one object never affects another
- Object fields get default values (`null`, `0`, `false`) automatically if not set — unlike local variables, which must be initialized

**Implementation notes:**
> Built a `Car` class with fields (`brand`, `model`, `year`, `isRunning`) and methods (`startEngine()`, `displayInfo()`). Created multiple independent car objects, stored them in an array, and confirmed passing an object into a method lets that method modify the object's fields directly (reference behavior, same as arrays in `_9_Methods.java`).

---

### 2️⃣ `_2_Constructors.java`
**Concept:** Special methods that run automatically at object creation to initialize fields

**Why it matters:** Manually setting every field after creation (like in `_1_ClassesAndObjects`) is error-prone — constructors let you guarantee an object starts in a valid, fully-initialized state the moment it's created.

**Syntax formula:**
```java
class Book {
    String title;
    Book(String title) {
        this.title = title;
    }
}
```

**Key rules / gotchas:**
- Writing any constructor removes Java's free default (no-arg) constructor — you must write one yourself if you still want `new Book()` to work
- Constructor overloading lets multiple creation patterns coexist, resolved by argument count/type
- `this(...)` chains one constructor to another, but must be the very first line

**Implementation notes:**
> Built a `Book` class with 4 overloaded constructors, including one chaining to another via `this(...)`. Confirmed via console print statements exactly which constructor ran for each object, and traced through the chaining behavior (title-only constructor internally calls the title+pages constructor with a default page count).

---

### 3️⃣ `_3_ThisKeyword.java`
**Concept:** A reference to the current object, with several distinct use cases beyond constructors

**Why it matters:** `this` shows up constantly in real Java code — for resolving naming conflicts, enabling method chaining, and passing an object's own reference elsewhere. Understanding all its forms prevents confusion later when reading unfamiliar codebases.

**Syntax formula:**
```java
class Student {
    String name;
    Student setName(String name) {
        this.name = name;
        return this;  // enables chaining
    }
}
```

**Key rules / gotchas:**
- `this` is optional when there's no naming conflict — but required to resolve field-vs-parameter (or field-vs-local-variable) shadowing
- Returning `this` from a method enables method chaining (`obj.setName(...).setAge(...)`)
- `this` cannot exist in a `static` context — there's no "current object" for a class-level method to refer to

**Implementation notes:**
> Covered self-reference, resolving both parameter and local-variable shadowing, passing `this` into a `Library` class's `registerStudent()` method, and building chainable setters. This directly previewed why static methods behave differently — set up the next topic naturally.

---

### 4️⃣ `_4_Encapsulation.java`
**Concept:** Hiding internal fields behind private access, exposing controlled read/write through public methods

**Why it matters:** Public fields (as used in `_1_ClassesAndObjects`) allow any external code to set invalid state with zero resistance. Encapsulation is the first of the four OOP pillars and the foundation for building objects that protect their own integrity.

**Syntax formula:**
```java
class BankAccount {
    private double balance;

    double getBalance() { return balance; }
    void setBalance(double newBalance) {
        if (newBalance >= 0) balance = newBalance;
    }
}
```

**Key rules / gotchas:**
- A setter with no validation logic barely improves on a public field — the real value of encapsulation is in what the setter *rejects*
- Not every field needs a setter — omitting one entirely makes a field effectively read-only after construction
- `final` fields (like an account number) are a stronger guarantee than just "no setter" — genuinely locked after the constructor runs

**Implementation notes:**
> Built a side-by-side comparison: `BankAccountUnsafe` (public field, allowed a negative balance) vs `BankAccountSafe` (private field, validated setter, plus meaningful action methods `deposit()`/`withdraw()` with their own rejection logic for invalid amounts). Confirmed the compiler itself blocks direct external field access once a field is private.

---

### 5️⃣ `_5_StaticVsInstance.java`
**Concept:** Instance members (belong to each object) vs static members (belong to the class itself, shared across all objects)

**Why it matters:** Every field/method up to this point was instance-level. Static members introduce shared, class-wide state and behavior — critical for object counters, utility methods, and constants shared across every instance.

**Syntax formula:**
```java
class Employee {
    static int employeeCount = 0;  // one shared copy across ALL objects
    String name;                    // unique per object

    Employee(String name) {
        this.name = name;
        employeeCount++;
    }

    static void printCount() {
        System.out.println(employeeCount);
    }
}
```

**Key rules / gotchas:**
- Static fields are shared — changing one through the class name changes what every object "sees," since there's only one copy in memory
- Static methods cannot access instance fields directly — no `this`, no object context to refer to
- Static blocks run exactly once, automatically, when the class is first loaded — useful for one-time setup

**Implementation notes:**
> Built an `Employee` class with a static `employeeCount` tracker that increments in the constructor, a static `companyName` field shared across all objects, a static utility method (`calculateBonus`) that needs no object at all, and a static initialization block that runs once on class load.

---

### 6️⃣ `_6_Inheritance.java`
**Concept:** Creating a child class that reuses and extends a parent class's fields and methods via `extends`

**Why it matters:** Inheritance is the second OOP pillar — it's how Java avoids duplicating code across related classes, and sets up the mechanism (`super`, overriding) that polymorphism depends on.

**Syntax formula:**
```java
class Animal {
    String name;
    Animal(String name) { this.name = name; }
    void makeSound() { System.out.println("generic sound"); }
}

class Dog extends Animal {
    Dog(String name) { super(name); }
    @Override
    void makeSound() { System.out.println("Woof!"); }
}
```

**Key rules / gotchas:**
- `super(...)` must be the very first line in a child constructor if used explicitly
- `@Override` isn't required but protects against silently creating an unrelated method via a typo or mismatched signature
- Java only allows single class inheritance — one `extends` only, which is exactly why interfaces exist

**Implementation notes:**
> Built an `Animal → Dog → Puppy` multi-level inheritance chain, demonstrated full method overriding (`Cat` fully replacing `makeSound()`) vs extending via `super.makeSound()` (`Dog` calling the parent version then adding its own line). Confirmed constructor call order flows from grandparent down to child automatically.

---

### 7️⃣ `_7_Polymorphism.java`
**Concept:** One interface, many implementations — a parent-type reference can hold different child-type objects, each responding to the same method call differently

**Why it matters:** This is the third OOP pillar, and arguably the one that makes OOP genuinely powerful rather than just organizational — it's what lets you write code against an abstraction instead of a concrete type.

**Syntax formula:**
```java
Animal myAnimal = new Dog();  // upcasting
myAnimal.makeSound();          // runs Dog's version, not Animal's

if (myAnimal instanceof Dog d) {
    d.fetch();  // safe downcast
}
```

**Key rules / gotchas:**
- The reference type controls what's *callable*; the actual object type controls what *runs*
- Downcasting without an `instanceof` check first risks a runtime `ClassCastException`
- The real payoff: one loop over `Animal[]` correctly handles Dogs, Cats, and any future subtype without ever needing to know their specific type

**Implementation notes:**
> Contrasted compile-time polymorphism (method overloading, recap) with runtime polymorphism (overriding + dynamic dispatch). Looped through an `Animal[]` array containing mixed subtypes, each correctly calling its own overridden `makeSound()`. Demonstrated safe downcasting with `instanceof` (including modern pattern-matching syntax) and deliberately triggered a `ClassCastException` to see the failure mode firsthand.

---

### 8️⃣ `_8_AbstractClasses.java`
**Concept:** Classes that cannot be instantiated directly and can declare methods with no implementation, forcing child classes to provide one

**Why it matters:** The first half of the fourth pillar, Abstraction — a way to define a shared contract while still allowing some shared concrete behavior.

**Syntax formula:**
```java
abstract class Shape {
    abstract double calculateArea();  // no body - subclasses must implement

    void displayInfo() {  // shared, concrete method
        System.out.println("Area: " + calculateArea());
    }
}
```

**Key rules / gotchas:**
- An abstract class can never be instantiated directly, even though it can have a constructor (runs only via `super()` from a subclass)
- Every abstract method must eventually be implemented by some concrete subclass, enforced at compile time
- Mixes "must implement" (abstract methods) with "already implemented, shared" (concrete methods) — the key difference from interfaces

**Implementation notes:**
> Built a `Shape → Circle/Rectangle/Triangle` hierarchy where each shape provides its own `calculateArea()`, but all inherit a shared `displayInfo()` method for free. Confirmed polymorphism works cleanly on top of an abstract base (`Shape[]` array calculating each area correctly).

---

### 9️⃣ `_9_Interfaces.java`
**Concept:** A pure contract a class agrees to fulfill via `implements`, with support for multiple interfaces per class

**Why it matters:** Java doesn't allow multiple inheritance of classes, but interfaces are how it achieves a similar effect safely — extremely common in real-world Java APIs and frameworks.

**Syntax formula:**
```java
interface Drivable {
    void startEngine();
    default void honk() { System.out.println("Beep!"); }
    static void printRules() { System.out.println("Drive safely"); }
}

class Car implements Drivable {
    public void startEngine() { System.out.println("Vroom"); }
}
```

**Key rules / gotchas:**
- A class can implement as many interfaces as needed, but still only extend one class — the single biggest practical reason interfaces exist
- Interface fields are always implicitly `public static final`, even without writing those keywords
- `default` methods provide free shared behavior that implementing classes can still override

**Implementation notes:**
> Built `Drivable` and `Flyable` interfaces, with `FlyingCar` implementing both at once (impossible via class inheritance alone). Covered `default` methods (`honk()`, overridden by `Motorcycle`) and `static` interface methods (`printDrivingRules()`), plus `instanceof` checks against interface types.

---

### 🔟 `_10_AccessModifiers.java`
**Concept:** `public`, `private`, `protected`, and default (package-private) visibility levels

**Why it matters:** Encapsulation depends entirely on choosing the right access level — this topic goes deeper than the `private`-only usage seen so far, including how `protected` interacts with inheritance.

**Syntax formula:**
```java
public String brand;          // accessible everywhere
private String serialNumber;  // only within this class
int modelYear;                 // default - only within same package
protected String engineType;   // same package + subclasses in other packages
```

**Key rules / gotchas:**
- Top-level classes can only be `public` or default — `private class`/`protected class` isn't valid at that level
- `protected` and default look identical when everything's in the same package; the real difference only shows across package boundaries
- `protected` is specifically about inheritance — the one modifier that privileges subclasses even in different packages

**Implementation notes:**
> Built a `Vehicle` class demonstrating all four access levels at once, with `Car extends Vehicle` proving protected field access via inheritance. Documented (but didn't fully test in one file) how to verify true cross-package `protected`/default behavior with a second package.

---

### 1️⃣1️⃣ `_11_Enums.java`
**Concept:** A fixed, named set of constants, optionally with their own fields, constructors, and methods

**Why it matters:** Enums are the correct tool whenever a variable should only ever hold one of a small, known set of values — far safer than using raw Strings or ints for the same purpose.

**Syntax formula:**
```java
enum Day { MONDAY, TUESDAY, WEDNESDAY /* ... */ }

enum Planet {
    EARTH(9.8, 149.6);
    private final double gravity;
    private final double distanceFromSun;
    Planet(double g, double d) { gravity = g; distanceFromSun = d; }
}
```

**Key rules / gotchas:**
- Enum constructors are always implicitly private — you can never call `new Planet(...)` yourself
- `ordinal()` reflects declaration order only — never rely on it for anything meaningful like storage
- `valueOf()` throws `IllegalArgumentException` on no match, unlike a safe `null` return

**Implementation notes:**
> Covered simple enums (`Day`), enums with fields/constructors carrying real data (`Planet`, with gravity and distance), and constant-specific method bodies (`TrafficLight`, where each color implements its own `getAction()`). Hit and resolved a file-encoding issue caused by a special Unicode character (`²`) in a comment, which cascaded into unrelated-looking compiler errors — a good real debugging lesson in how one bad character can break far more than expected.

---

### 1️⃣2️⃣ `_12_EqualsHashCodeToString.java`
**Concept:** Overriding Java's default `equals()`, `hashCode()`, and `toString()` behavior for custom classes

**Why it matters:** Without overriding these, `==`-style content comparison fails on custom objects (same issue as Strings, but now on your own classes) and printing an object shows an unreadable memory address. This also directly sets up correct `HashMap`/`HashSet` behavior in `03-collections`.

**Syntax formula:**
```java
@Override
public boolean equals(Object obj) {
    if (this == obj) return true;
    if (obj == null || getClass() != obj.getClass()) return false;
    Person other = (Person) obj;
    return age == other.age && Objects.equals(name, other.name);
}

@Override
public int hashCode() {
    return Objects.hash(name, age);
}
```

**Key rules / gotchas:**
- If two objects are `.equals()`, they **must** have the same `hashCode()` — breaking this contract silently corrupts `HashMap`/`HashSet` behavior
- `Objects.hash()` should use the exact same fields `equals()` compares — mismatches are the most common way this contract gets violated
- This is arguably the most consequential override pair in the entire OOP folder, precisely because it sets up `03-collections`

**Implementation notes:**
> Directly demonstrated the real-world breakage: a `HashSet` failing to deduplicate identical-content objects without proper overrides (size 2 instead of 1), then fixed with a correctly overridden `Person` class (size 1, as expected). Also proved a `HashMap` lookup with a different-but-equal object instance as the key still correctly finds its value.

---

### 1️⃣3️⃣ `_13_Composition.java`
**Concept:** Building complex objects out of other objects ("has-a" relationships) as an alternative to inheritance ("is-a")

**Why it matters:** A well-known real-world design principle is "favor composition over inheritance" — this topic shows why, and when each approach actually fits better.

**Syntax formula:**
```java
class Car {
    Engine engine;  // Car HAS-A Engine, not IS-A Engine
    void start() { engine.start(); }  // delegation
}
```

**Key rules / gotchas:**
- The "is-a" test decides it — if a subclass wouldn't genuinely be a specialized type of its parent, that's a signal to use composition instead
- Composition allows swapping parts at runtime (`car.setEngine(newEngine)`) — something inheritance can never do once compiled
- The classic Duck/FlyBehavior example is a real, widely-used design pattern (Strategy Pattern)

**Implementation notes:**
> Built a `Car` composed of `Engine`, `GPS`, and `SoundSystem` objects, demonstrating delegation (Car doesn't implement engine logic itself, it asks the Engine object to do it) and runtime engine-swapping. Also built the Duck/FlyBehavior example showing why inheriting a "fly" behavior onto a `RubberDuck` would be a design mistake, solved instead by composing in an interchangeable `FlyBehavior` object.

---

### 1️⃣4️⃣ `_14_OOPCapstone.java`
**Concept:** A single design exercise combining Encapsulation, Inheritance, Polymorphism, and Abstraction together

**Why it matters:** Each pillar so far has been practiced in isolation — real code combines all four at once. This capstone is the actual test of whether the concepts are understood, not just memorized individually.

**Implementation notes:**
> Modeled a small Employee Management System: `Employee` (abstract, encapsulated fields) → `Manager`/`Developer` (inheritance, each with its own `calculatePay()` override — polymorphism). Added a `Mentor` interface implemented only by `Manager` (a capability, not an identity — proving interfaces model "can-do" separately from "is-a"). Composed an `Address` object into `Employee` (has-a, not is-a). Used a `Department` enum for safe fixed categories, a static `employeeCount` shared across all employees, and properly overridden `equals()`/`hashCode()`/`toString()` — proven working by an `ArrayList.contains()` call correctly recognizing a logically-duplicate `Developer` object. This single file ties together all 13 preceding topics into one coherent, realistic design.

---

## 🧠 Skills Demonstrated

Now that `02-oop` is complete, this folder shows:
- Full command of all four OOP pillars — Encapsulation, Inheritance, Polymorphism, Abstraction — both in isolation and combined
- Understanding of static vs instance state, and when each is the correct choice
- Safe, correct use of interfaces alongside inheritance, including the judgment to use each where it actually fits
- Proper object identity handling (`equals()`/`hashCode()`/`toString()`) and why it matters for real collection behavior
- Design judgment: recognizing "is-a" vs "has-a" relationships, and choosing composition over inheritance when appropriate
- Practical debugging experience — traced a file-encoding issue back to a single Unicode character causing a cascading, misleading error list
- The ability to design and build a multi-class system from scratch (the capstone) rather than only completing isolated exercises

---

## 📝 How to Use This File

After completing each program:
1. Check its box in the **Progress Tracker** table above
2. Replace its `Implementation notes` placeholder with 2–4 sentences on what the code does and what clicked (or didn't)
3. Commit both the `.java` file and this updated `StudentGradeManager.md` together

This log feeds directly into the top-level portfolio `StudentGradeManager.md` once all phases are complete.

---

## ➡️ Next Up

`02-oop` is complete. Moving to **`03-collections`**, starting with **Lists (ArrayList, LinkedList)**.