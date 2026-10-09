# `_14_OOPCapstone.java`

## Concept
The final capstone — a single, cohesive Employee Management System design combining all 13 preceding `02-oop` topics: Encapsulation, Inheritance, Polymorphism, Abstraction, Interfaces, Composition, Enums, Static members, and proper `equals()`/`hashCode()`/`toString()`.

## Full Line-by-Line Breakdown

### `import java.util.ArrayList;` / `import java.util.Objects;`
Imports `ArrayList` (used to demonstrate `equals()`/`hashCode()` working correctly in a real collection) and `Objects` (used for the null-safe `equals()`/`hash()` helper methods).

### `public class _14_OOPCapstone {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### CAPSTONE OVERVIEW
No executable code — a summary comment mapping each OOP concept to exactly where it appears in this design, serving as a table of contents for everything that follows.

---

### SECTION 1: Creating Objects

**`Address addr1 = new Address("123 Main St", "Austin", "TX");` / `Address addr2 = new Address("456 Oak Ave", "Seattle", "WA");`**
Two independent `Address` objects — these will be **composed into** `StaffMember` objects, not inherited.

**`Manager manager = new Manager("Alice Chen", 95000, addr1, Department.ENGINEERING, 8);`**
Creates a `Manager` — passing a name, salary, an `Address` object, a `Department` enum constant, and a team size.

**`Developer dev1 = new Developer("Bob Singh", 78000, addr2, Department.ENGINEERING, "Java");` / `Developer dev2 = new Developer("Cara Lopez", 82000, addr1, Department.PRODUCT, "Python");`**
Two `Developer` objects, each with their own primary programming language.

**`StaffMember.getEmployeeCount()`**
Calls a **static** method via the class name — prints `3`, since three `StaffMember`-derived objects have been constructed so far, each incrementing the shared counter.

---

### SECTION 2: Encapsulation

**`manager.getName()`**
Calls a public getter to read the private `name` field.

**`manager.setBaseSalary(100000);`**
A valid raise — the setter's validation (`newSalary >= 0`) passes, and the salary updates.

**`manager.setBaseSalary(-500);`**
An invalid attempt — the setter rejects it, printing a message and leaving the salary unchanged from the previous valid update.

---

### SECTION 3: Polymorphism

**`StaffMember[] staff = { manager, dev1, dev2 };`**
An array typed as the abstract parent `StaffMember`, holding two different concrete subtypes.

**`for (StaffMember e : staff) { System.out.printf(..., e.getName(), e.getDepartment(), e.calculatePay()); }`**
A single loop that correctly calls each object's **own** overridden `calculatePay()` — `Manager` uses a team-size-based bonus formula, `Developer` uses a flat stipend formula — without the loop needing to know which specific subtype it's currently processing.

---

### SECTION 4: Abstraction
No executable code — a commented-out line (`StaffMember employee = new StaffMember(...);`) showing what would be a compile error: `StaffMember` is `abstract` and can never be instantiated directly, only through its concrete subclasses.

---

### SECTION 5: Interfaces

**`for (StaffMember e : staff) { if (e instanceof Mentor mentor) { mentor.mentor(); } else { ... } }`**
Uses modern pattern-matching `instanceof` to check whether each staff member **also** implements the separate `Mentor` interface. Since only `Manager` implements `Mentor`, this correctly identifies `manager` as a mentor while printing a "not mentoring" message for both developers — demonstrating that `Mentor` is a **capability**, not a shared identity across the whole `StaffMember` hierarchy.

---

### SECTION 6: Inheritance

**`manager.displayInfo();`**
Calls a method **inherited** from `StaffMember` — never rewritten in `Manager` itself.

**`manager.holdMeeting();`**
Calls a method that exists **only** on `Manager`, not inherited from `StaffMember` at all.

**`dev1.displayInfo();` / `dev1.writeCode();`**
Same pattern applied to `Developer` — one inherited shared method, one subclass-specific method.

---

### SECTION 7: Composition

**`dev1.getAddress()`**
Returns the `Address` **object** contained inside `dev1` — when concatenated into a `println`, this automatically calls `Address`'s own overridden `toString()`, printing something like `"456 Oak Ave, Seattle, WA"`. This proves `StaffMember` HAS-A `Address`, rather than somehow being one.

---

### SECTION 8: Enums

**`for (Department d : Department.values()) { System.out.println("- " + d); }`**
Loops through every constant in the `Department` enum, printing each one — proving the fixed, safe set of category options this enum represents.

---

### SECTION 9: equals(), hashCode(), toString()

**`Developer dev1Duplicate = new Developer("Bob Singh", 78000, addr2, Department.ENGINEERING, "Java");`**
A **separate object**, but with field values identical to `dev1`.

**`dev1 == dev1Duplicate`**
Returns `false` — different objects in memory, exactly as expected for `==`.

**`dev1.equals(dev1Duplicate)`**
Returns `true` — `StaffMember`'s overridden `equals()` compares `name` and `department`, both of which match here.

**`ArrayList<StaffMember> allEmployees = new ArrayList<>(); allEmployees.add(dev1);`**
Adds only the original `dev1` object to the list.

**`allEmployees.contains(dev1Duplicate)`**
Returns `true` — even though `dev1Duplicate` was **never actually added** to the list, `.contains()` correctly recognizes it as a logical match to `dev1`, purely because `equals()`/`hashCode()` are properly overridden. This is the exact real-world payoff first demonstrated in `_12_EqualsHashCodeToString.java`, now proven inside a realistic, complete system.

---

### SECTION 10: Static

**`StaffMember.getEmployeeCount()`**
Printed again at the very end — now reflecting `4` total employees, since `dev1Duplicate`'s constructor also ran and incremented the shared counter, **regardless** of the fact that it's logically "equal" to an existing employee. This distinguishes object *count* (a static, class-wide fact) from object *equality* (a per-object comparison) — two related but genuinely different concepts.

---

### The `Department` Enum

```java
enum Department {
    ENGINEERING, PRODUCT, SALES, HR
}
```
A simple, fixed set of constants — recap of `_11_Enums.java`'s basic pattern, used here as a safe alternative to raw category Strings.

---

### The `Address` Class (Composition Target)

```java
class Address {
    private final String street;
    private final String city;
    private final String state;

    Address(String street, String city, String state) {
        this.street = street;
        this.city = city;
        this.state = state;
    }

    @Override
    public String toString() {
        return street + ", " + city + ", " + state;
    }
}
```
All three fields are `private final` — set once at construction, never changed afterward. `toString()` is overridden so that printing an `Address` (or concatenating one into a String, as `StaffMember` does) produces a clean, readable line rather than a memory-address string.

---

### The `Mentor` Interface

```java
interface Mentor {
    void mentor();
}
```
A minimal interface with one abstract method — deliberately kept separate from the `StaffMember` class hierarchy, since "can mentor" is a capability some staff members have and others don't, not a shared identity trait.

---

### The `StaffMember` Abstract Class

**Fields:**
```java
private String name;
private double baseSalary;
private final Address address;
private final Department department;
private static int employeeCount = 0;
```
`name` and `baseSalary` are mutable instance fields (encapsulated behind getters/setters). `address` and `department` are `final` — set once at construction, never reassigned. `employeeCount` is `static` — one shared copy across every `StaffMember` ever created, regardless of subtype.

**Constructor:**
```java
StaffMember(String name, double baseSalary, Address address, Department department) {
    this.name = name;
    this.baseSalary = baseSalary;
    this.address = address;
    this.department = department;
    employeeCount++;
}
```
Initializes all four fields, then increments the shared static counter — this runs every time **any** subclass (`Manager` or `Developer`) is constructed, via their `super(...)` calls.

**Setter with validation:**
```java
void setBaseSalary(double newSalary) {
    if (newSalary >= 0) {
        this.baseSalary = newSalary;
    } else {
        System.out.println("Rejected: salary cannot be negative.");
    }
}
```
Recap of the Encapsulation pattern — rejects invalid values rather than blindly accepting them.

**Abstract method:**
```java
abstract double calculatePay();
```
No body — every concrete subclass **must** provide its own implementation, enforced by the compiler.

**Concrete shared method:**
```java
void displayInfo() {
    System.out.println(name + " | " + department + " | Base salary: $" + baseSalary);
}
```
Fully implemented once here, inherited automatically by every subclass — no need to repeat this logic in `Manager` or `Developer`.

**equals()/hashCode()/toString():**
```java
@Override
public String toString() {
    return "StaffMember{name='" + name + "', department=" + department + "}";
}

@Override
public boolean equals(Object obj) {
    if (this == obj) return true;
    if (obj == null || getClass() != obj.getClass()) return false;
    StaffMember other = (StaffMember) obj;
    return Objects.equals(name, other.name) && department == other.department;
}

@Override
public int hashCode() {
    return Objects.hash(name, department);
}
```
The exact same defensive pattern from `_12_EqualsHashCodeToString.java` — fast-path reference check, null/class check, then field comparison. Note `equals()` compares `name` **and** `department` — deliberately not `baseSalary` or `address`, meaning two employees with the same name and department are considered "equal" regardless of what they earn or where they live, a deliberate design choice for this particular system.

---

### The `Manager` Class

```java
class Manager extends StaffMember implements Mentor {
    private int teamSize;

    Manager(String name, double baseSalary, Address address, Department department, int teamSize) {
        super(name, baseSalary, address, department);
        this.teamSize = teamSize;
    }

    @Override
    double calculatePay() {
        return getBaseSalary() + (teamSize * 500);
    }

    void holdMeeting() {
        System.out.println(getName() + " is holding a team meeting with " + teamSize + " people.");
    }

    @Override
    public void mentor() {
        System.out.println(getName() + " is mentoring junior team members.");
    }
}
```
`extends StaffMember` (inheritance — a Manager genuinely **is** a StaffMember) **and** `implements Mentor` (a separate capability) — both at once, on the same class declaration. `calculatePay()` provides a manager-specific bonus formula based on team size. `holdMeeting()` is a method that exists only here, not inherited from `StaffMember`. `mentor()` fulfills the `Mentor` interface's contract.

---

### The `Developer` Class

```java
class Developer extends StaffMember {
    private String primaryLanguage;

    Developer(String name, double baseSalary, Address address, Department department, String primaryLanguage) {
        super(name, baseSalary, address, department);
        this.primaryLanguage = primaryLanguage;
    }

    @Override
    double calculatePay() {
        return getBaseSalary() + 2000;
    }

    void writeCode() {
        System.out.println(getName() + " is writing code in " + primaryLanguage + ".");
    }
}
```
Only `extends StaffMember` — **not** `Mentor`, deliberately, to prove in Section 5 that not every staff member shares that capability. `calculatePay()` uses a completely different formula from `Manager`'s (a flat stipend instead of a per-team-member bonus), demonstrating genuine polymorphic variation.

## Key Design Decisions Worth Noticing

1. **`Mentor` is an interface, not part of the inheritance chain** — because "can mentor" is a capability, not a type of employee. This is exactly the interface-vs-inheritance distinction from `_9_Interfaces.java`, applied in a realistic context.
2. **`Address` is composed in, not inherited** — a `StaffMember` is not a type of `Address`; it simply has one. Straight from `_13_Composition.java`.
3. **`equals()`/`hashCode()` prove themselves useful here**, not just in isolation — `ArrayList.contains()` correctly finds a logical duplicate `Developer` object, exactly the kind of real payoff `_12_EqualsHashCodeToString.java` was building toward.
4. **Static (`employeeCount`) and equality (`equals()`) measure genuinely different things** — the counter tracks how many objects were ever *constructed*, while equality tracks whether two objects are logically *the same*. Section 10 deliberately shows these can diverge: 4 objects constructed, but 2 of them considered "equal" to each other.

## Why This Structure Exists

Every one of the 13 preceding topics was practiced in isolation. Real code never works that way — a single well-designed class often needs encapsulation, might participate in inheritance, might implement an interface for an unrelated capability, might compose in other objects, and almost certainly needs correct `equals()`/`hashCode()`/`toString()` if it will ever end up in a collection. This capstone is the actual test of whether these concepts were understood as a *system* rather than as 13 disconnected facts — and it's exactly the kind of design thinking real-world Java codebases require.

---

**This completes `02-oop` in full.** Every topic from Classes and Objects through this capstone has been built, explained, and tied together into one working design.