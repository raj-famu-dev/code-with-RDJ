# `_5_StaticVsInstance.java`

## Concept
Instance members (belong to each object separately) vs static members (belong to the class itself, shared across all objects) — including static fields, methods, constants, utility methods, and static initialization blocks.

## Full Line-by-Line Breakdown

### `public class _5_StaticVsInstance {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: Instance Members (Recap)

**`Employee emp1 = new Employee("Alice", 50000);` / `Employee emp2 = new Employee("Bob", 60000);`**
Two independent objects, each with their own `name` and `salary`.

**The two `println` lines**
Confirm each object holds separate data — recap of the same independence proven back in `_1_ClassesAndObjects.java`.

---

### SECTION 2: Static Fields

**`Employee.companyName`**
Accessed through the **class name** directly (`Employee.companyName`), not through an object (`emp1.companyName`) — this is the key syntactic tell that a field is static: it doesn't belong to any single object, so there's no reason to access it via one.

**`Employee.companyName = "TechCorp International";`**
Changes the value through the class.

**`emp1.companyName` / `emp2.companyName`**
Even though these are accessed via object references here (which Java actually allows, though it's discouraged style), both print the **updated** value — proving there is only **one** shared `companyName` in memory, not a separate copy per object.

---

### SECTION 3: Static Fields For Tracking

**`Employee.employeeCount`**
Printed before creating any new employees in this section — shows however many were already created (from `emp1` and `emp2` in Section 1).

**`Employee emp3 = new Employee("Charlie", 55000);` / `Employee emp4 = new Employee("Dana", 58000);`**
Two more objects created — each time, the constructor runs `employeeCount++;`.

**`Employee.employeeCount` (printed again)**
Now shows a higher number, confirming the shared counter incremented correctly across every object created so far, not just the two most recent ones.

---

### SECTION 4: Static Methods

**`Employee.printCompanyInfo();`**
Called directly on the **class**, with no `Employee` object needed at all.

**The commented-out `System.out.println(name);`**
Included specifically to show what would happen if attempted inside a static method: a **compile error**, since `name` is an instance field, and a static method has no specific object context to know *whose* `name` to use.

---

### SECTION 5: Instance Methods Can Access Both

**`emp1.displayFullInfo();`**
Calls an **instance** method, which internally references both `name` (instance field, unique to `emp1`) and `companyName` (static field, shared). This direction always works — instance methods have full access to both instance and static members, since they're already running "on behalf of" a specific object.

---

### SECTION 6: Static Constants

**`Employee.MAX_EMPLOYEES`**
A constant combining `static` and `final` — shared across the whole class, and permanently unchangeable after being set. The commented-out reassignment attempt would be a compile error, same as any other `final` variable.

---

### SECTION 7: Static Utility Methods

**`Employee.calculateBonus(50000, 0.1);`**
Called directly on the class — no `Employee` object was ever created for this specific calculation, because the method doesn't need one. It's a **pure function**: given the same two inputs, it always produces the same output, entirely independent of any object's state.

---

### SECTION 8: Static Blocks

**The two `println` lines in this section**
Print *after* the fact, but the comments make clear that a static block (defined in the class below) already ran **before** any of this code — specifically, the moment the `Employee` class was first loaded into memory, which happens automatically the first time it's referenced (in this case, all the way back at `emp1`'s creation in Section 1).

**`Employee.departments.size()`**
Confirms the static block actually did its job — the `departments` list was populated with 3 entries during that one-time setup, and this line proves that data persisted and is now accessible.

---

### SECTION 9: When To Use Static vs Instance
No new code — a decision guide summarizing when each is the right choice.

---

### The `Employee` Class Definition

**Instance fields:**
```java
String name;
double salary;
```
Each `Employee` object gets its own independent copy of these two fields.

**Static fields:**
```java
static String companyName = "TechCorp";
static int employeeCount = 0;
static final int MAX_EMPLOYEES = 1000;
static java.util.ArrayList<String> departments = new java.util.ArrayList<>();
```
All four belong to the **class**, not to any individual object — there is exactly one copy of each, shared by every `Employee` that will ever exist.

**Static block:**
```java
static {
    System.out.println("[Static block running - one-time setup]");
    departments.add("Engineering");
    departments.add("Sales");
    departments.add("HR");
}
```
This code has no method name and no explicit call anywhere — it runs **automatically**, exactly once, the very first time the `Employee` class is loaded by the JVM (which typically happens the first time it's referenced, such as the first `new Employee(...)` call). It's the ideal place to perform one-time setup for static fields that need more than a simple initial value.

**Constructor:**
```java
Employee(String name, double salary) {
    this.name = name;
    this.salary = salary;
    employeeCount++;
}
```
Sets the two instance fields as usual, then increments the **shared static counter** — this single line is what makes `employeeCount` accurately reflect the total number of `Employee` objects ever created, across the entire program.

**Instance method:**
```java
void displayFullInfo() {
    System.out.println(name + " works at " + companyName + ", earning " + salary);
}
```
Freely mixes an instance field (`name`, `salary`) with a static field (`companyName`) in the same line — this is always valid, since an instance method already has a specific object (`this`) to resolve instance fields against.

**Static method:**
```java
static void printCompanyInfo() {
    System.out.println("Company: " + companyName + ", Total employees: " + employeeCount);
}
```
Only references other **static** members (`companyName`, `employeeCount`) — it could never reference `name` or `salary` directly, since there's no object context inside a static method to resolve those against.

**Static utility method:**
```java
static double calculateBonus(double baseSalary, double percentage) {
    return baseSalary * percentage;
}
```
Doesn't touch **any** field, static or instance — it's a pure calculation based only on the parameters it receives, making it a textbook example of when `static` is the obviously correct choice.

## Key Rules / Gotchas Recap

- Static fields are **shared**, not copied — changing one through the class name changes what every object "sees," since there's genuinely only one copy in memory
- Static methods **cannot** access instance fields/methods directly — no `this`, no object context to resolve them against
- Instance methods **can** freely access both instance and static members, since they always have a specific object to work from
- Static blocks run exactly **once**, automatically, when the class is first loaded — useful for one-time setup that shouldn't repeat inside every constructor call
- `static final` together creates a genuine shared, unchangeable constant

## Why This Structure Exists

Every field and method up through `_4_Encapsulation.java` was instance-level. Static members introduce shared, class-wide state and behavior — essential for object counters, shared configuration values, utility methods that don't need any object's state, and constants meant to apply uniformly across every instance. This also directly explains *why* `this` (from the previous topic) cannot exist in a static context: there's no specific object for it to refer to.