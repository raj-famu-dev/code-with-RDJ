# `_9_Interfaces.java`

## Concept
Interfaces — a pure contract a class agrees to fulfill via `implements`, supporting multiple interfaces per class, default methods, static interface methods, and implicit constants.

## Full Line-by-Line Breakdown

### `public class _9_Interfaces {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is An Interface?
No executable code — just the conceptual framing, plus a commented-out example showing that interfaces, like abstract classes, can never be instantiated directly.

---

### SECTION 2: A Class Implementing An Interface

**`Sedan sedan = new Sedan();`**
Creates an object of `Sedan`, a class that `implements Drivable`.

**`sedan.startEngine();` / `sedan.stopEngine();`**
Calls the two methods `Sedan` was **required** to implement, since `Drivable` declares them as abstract (no body) method signatures.

---

### SECTION 3: A Class Can Implement Multiple Interfaces

**`AirCar airCar = new AirCar();`**
Creates an object of `AirCar` — a class implementing **two** interfaces at once: `Drivable` and `Flyable`.

**`airCar.startEngine();` / `airCar.stopEngine();`**
Fulfills the `Drivable` contract.

**`airCar.fly();` / `airCar.land();`**
Fulfills the **separate** `Flyable` contract, at the same time, on the same object.

**Why this matters:** Java only permits a class to `extend` **one** parent class, but a class can `implement` as many interfaces as needed — this is exactly the workaround for that single-inheritance limitation, directly foreshadowed back in `_6_Inheritance.java`.

---

### SECTION 4: Polymorphism With Interfaces

**`Drivable[] vehicles = { new Sedan(), new AirCar(), new Motorbike() };`**
An array typed as the **interface** `Drivable`, holding three different concrete implementing classes.

**`for (Drivable v : vehicles) { v.startEngine(); }`**
A single loop correctly calls each vehicle's own `startEngine()` implementation — the same polymorphism mechanic as `_7_Polymorphism.java` and `_8_AbstractClasses.java`, but now built on an **interface** type instead of a class or abstract class.

---

### SECTION 5: Default Methods

**`sedan.honk();`**
`Sedan` never wrote its own `honk()` method — this call uses `Drivable`'s **default** implementation directly, inherited automatically.

**`airCar.honk();`**
Same — `AirCar` also never overrode `honk()`, so it uses the shared default too.

**`Motorbike motorbike = new Motorbike(); motorbike.honk();`**
`Motorbike`, however, **does** provide its own `honk()` (see class definition below), so this call runs `Motorbike`'s specific version instead of the interface's default one — proving default methods can be selectively overridden per implementing class.

---

### SECTION 6: Static Methods In Interfaces

**`Drivable.printDrivingRules();`**
Called directly on the **interface name** itself — not on `sedan`, not on `airCar`, not on any object at all. Static interface methods belong to the interface, exactly like static class methods belong to their class.

---

### SECTION 7: Interface Constants

**`Drivable.MAX_SPEED_LIMIT`**
Accessed via the interface name, printing `120`. The commented-out reassignment attempt (`Drivable.MAX_SPEED_LIMIT = 200;`) would be a compile error — any field declared inside an interface is **automatically** `public static final`, whether or not you write those keywords yourself.

---

### SECTION 8: Interface vs Abstract Class — Key Differences
No new executable code — a summarized comparison. Abstract classes support constructors and instance fields with any access level, but only single inheritance; interfaces traditionally have no constructors and always-constant fields, but support multiple implementation per class. Modern Java's `default`/`static` methods have blurred some of the old distinction, but the **multiple implementation** capability remains the single biggest practical reason to reach for an interface over an abstract class.

---

### SECTION 9: instanceof Works With Interfaces Too

**`Drivable someVehicle = new AirCar();`**
Declared as the `Drivable` interface type, but actually holding an `AirCar` object.

**`if (someVehicle instanceof Flyable) { Flyable flying = (Flyable) someVehicle; flying.fly(); ... }`**
Checks whether this particular `Drivable` object **also** happens to implement `Flyable` — since `AirCar` implements both interfaces, this check passes, allowing a safe downcast to call `fly()`, a method that isn't part of the `Drivable` contract at all.

---

### SECTION 10: When To Use An Interface vs Abstract Class
No new code — a decision guide. Interfaces suit unrelated classes sharing a capability (not identity) or needing multiple contracts fulfilled at once; abstract classes suit a genuine "is-a" relationship with shared state.

---

### The `Drivable` Interface

```java
interface Drivable {
    int MAX_SPEED_LIMIT = 120;

    void startEngine();
    void stopEngine();

    default void honk() {
        System.out.println("Beep beep! (default horn sound)");
    }

    static void printDrivingRules() {
        System.out.println("Drive safely. Max speed limit: " + MAX_SPEED_LIMIT);
    }
}
```
`MAX_SPEED_LIMIT` — an implicit `public static final int`. `startEngine()`/`stopEngine()` — abstract method signatures, no body, every implementing class must supply these. `honk()` — a `default` method with a real body; implementing classes inherit this behavior automatically but may override it. `printDrivingRules()` — a `static` method belonging to the interface itself, callable without any implementing object at all.

### The `Flyable` Interface

```java
interface Flyable {
    void fly();
    void land();
}
```
A separate, smaller contract with no relationship to `Drivable` at all — purely a capability that some classes might additionally have.

---

### The Implementing Classes

```java
class Sedan implements Drivable {
    @Override
    public void startEngine() { System.out.println("Sedan engine started."); }
    @Override
    public void stopEngine() { System.out.println("Sedan engine stopped."); }
}
```
Implements only `Drivable`, providing both required methods. `honk()` is left unimplemented here, so it falls back to `Drivable`'s default.

```java
class Motorbike implements Drivable {
    @Override
    public void startEngine() { System.out.println("Motorbike engine started."); }
    @Override
    public void stopEngine() { System.out.println("Motorbike engine stopped."); }

    @Override
    public void honk() {
        System.out.println("Beep! (a much smaller horn sound)");
    }
}
```
Also implements only `Drivable`, but this time **does** override `honk()` with its own version — proving default methods are optional to override, not mandatory to use as-is.

```java
class AirCar implements Drivable, Flyable {
    @Override
    public void startEngine() { System.out.println("AirCar engine started."); }
    @Override
    public void stopEngine() { System.out.println("AirCar engine stopped."); }
    @Override
    public void fly() { System.out.println("AirCar is now airborne!"); }
    @Override
    public void land() { System.out.println("AirCar has landed."); }
}
```
Implements **both** `Drivable` and `Flyable` simultaneously, separated by a comma after `implements` — this single line is the direct proof that Java's "no multiple class inheritance" rule doesn't apply to interfaces.

## Key Rules / Gotchas Recap

- A class can implement as many interfaces as needed, but still only extend **one** class — the single biggest practical reason interfaces exist
- Interface fields are always implicitly `public static final`, even without writing those words — a common quiz trap
- `default` methods provide free, inherited behavior, but implementing classes can still override them individually
- `instanceof` and downcasting work identically with interface types as they do with class types

## Why This Structure Exists

Java doesn't allow multiple inheritance of classes, but interfaces are how it safely achieves a similar effect — extremely common in real-world Java APIs and frameworks, where a single class often needs to fulfill several unrelated behavioral contracts at once (like `AirCar` being both `Drivable` and `Flyable`). This directly contrasts with abstract classes from the previous topic, and choosing correctly between the two is a genuinely common real-world design decision.