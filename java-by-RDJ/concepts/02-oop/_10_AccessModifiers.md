# `_10_AccessModifiers.java`

## Concept
The four access modifiers — `public`, `protected`, default (package-private), and `private` — controlling visibility of classes, fields, methods, and constructors.

## Full Line-by-Line Breakdown

### `public class _10_AccessModifiers {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: The Four Access Modifiers
No executable code — just the conceptual framing, listing all four levels from most to least restrictive.

---

### SECTION 2: `private` — Most Restrictive

**`Vehicle vehicle = new Vehicle();`**
Creates a `Vehicle` object.

**`vehicle.displayDetails();`**
Works fine — `displayDetails()` is `public`.

**The commented-out `vehicle.serialNumber = "12345";`**
Would be a **compile error** if uncommented, since `serialNumber` is declared `private` in `Vehicle` — completely inaccessible from outside that class, even from `main()` in the same file.

**`vehicle.getSerialNumber()`**
The correct way to read the private field — through a `public` getter method, recapping the Encapsulation pattern from `_4_Encapsulation.java`.

---

### SECTION 3: `public` — Least Restrictive

**`vehicle.brand`**
Accessed **directly**, with no getter needed — since `brand` is declared `public`, it's accessible from literally anywhere.

**`vehicle.honk();`**
Calls a `public` method — no restrictions at all.

---

### SECTION 4: Default (Package-Private)

**`vehicle.performMaintenance();`**
Calls a method with **no access modifier written at all** — this makes it "default" or "package-private," meaning it's accessible only to other classes in the same package. Since this whole project uses no `package` statements, everything technically lives in one shared default package together, so this call succeeds here — but the comment explains it would fail if `main()` lived in a genuinely different, named package from `Vehicle`.

**`vehicle.modelYear`**
Same idea — a field with no modifier, accessible here only because of the shared default package.

---

### SECTION 5: `protected` — Intermediate Restriction

**`Truck truck = new Truck();`**
Creates a `Truck` object — a subclass of `Vehicle`.

**`truck.displayDetails();`**
Inherited `public` method — works as expected.

**`truck.performMaintenance();`**
Inherited default-access method — works here since everything shares the same default package.

**`truck.showProtectedInfo();`**
Calls `Truck`'s own method, which internally reads `Vehicle`'s `protected` field `engineType` directly. The key point (explained in the class definition below) is that this access is guaranteed to work specifically **because** `Truck` is a subclass of `Vehicle` — even if they lived in different packages, this particular access path would still succeed, which is exactly what distinguishes `protected` from plain default access.

---

### SECTION 6: Access Modifiers On Classes Themselves
No executable code — commented-out examples showing that a top-level class can only ever be `public` or default; `private class` or `protected class` at that level is a compile error, since those two modifiers only make sense for *members* inside a class, not for a whole top-level class itself.

---

### SECTION 7: Summary Table
A comment-only reference table, laid out as:

| Modifier | Same Class | Same Package | Subclass (diff package) | Everywhere |
|---|:---:|:---:|:---:|:---:|
| `private` | YES | NO | NO | NO |
| (default) | YES | YES | NO | NO |
| `protected` | YES | YES | YES | NO |
| `public` | YES | YES | YES | YES |

---

### SECTION 8: Why This Matters
No new code — real-world reasoning: `private` protects internal implementation details, `default` suits internal package-only helpers, `protected` shares details with subclasses across packages while still hiding them from unrelated code, and `public` defines your actual external API.

---

### SECTION 9: To Truly Test protected And default Across Packages
No new code — an honest acknowledgment that this single file can't fully demonstrate cross-package behavior, since everything here shares one default package. The comment gives explicit step-by-step instructions for setting up a genuine second package to prove the real distinction between `protected` and default access hands-on, if you want to verify it yourself.

---

### The `Vehicle` Class

```java
class Vehicle {
    public String brand = "Generic Brand";
    private String serialNumber = "SN-000000";
    int modelYear = 2024;
    protected String engineType = "Standard Engine";

    public void displayDetails() {
        System.out.println("Brand: " + brand + ", Serial: " + serialNumber);
    }

    public String getSerialNumber() {
        return serialNumber;
    }

    public void honk() {
        System.out.println(brand + " honks!");
    }

    void performMaintenance() {
        System.out.println(brand + " (model year " + modelYear + ") is being serviced.");
    }
}
```
Deliberately declares **one field and method at each of the four access levels**, side by side, so the contrast is immediately visible in one place: `brand` (public), `serialNumber` (private), `modelYear` (default — no keyword), `engineType` (protected). Same pattern applied to the methods: `displayDetails()`/`getSerialNumber()`/`honk()` are public, `performMaintenance()` has no modifier (default).

---

### The `Truck` Subclass

```java
class Truck extends Vehicle {
    void showProtectedInfo() {
        System.out.println("Engine type (inherited protected field): " + engineType);
    }
}
```
`extends Vehicle` establishes the inheritance relationship needed to demonstrate `protected` access specifically. Inside `showProtectedInfo()`, `engineType` is referenced directly with no `super.` or special syntax — it's simply accessible because `Truck` is a subclass, which is the entire point `protected` exists to guarantee, even across package boundaries (something this single-file setup can't fully prove, but the mechanism is identical regardless of package structure).

## Key Rules / Gotchas Recap

- `protected` and default access look **identical** when everything shares one package — the real difference only becomes visible across package boundaries
- Top-level classes can only be `public` or default — `private`/`protected` are invalid at that level, valid only for members inside a class
- `protected` is fundamentally about **inheritance** — it's the one modifier that specifically privileges subclasses, even in different packages, which default access does not do
- Since this project doesn't use `package` statements, every class effectively shares the same default package — meaning `protected` and default behave identically here, and true cross-package testing requires deliberately setting up a second package

## Why This Structure Exists

Encapsulation (the first OOP pillar, from `_4_Encapsulation.java`) depends entirely on choosing the right access level for each field and method — this topic goes deeper than the `private`-only usage seen there, filling in the full picture of `public`, `protected`, and default access, including how `protected` specifically interacts with inheritance in ways that plain default access does not.