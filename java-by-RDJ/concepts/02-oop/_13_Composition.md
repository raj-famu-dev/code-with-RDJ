# `_13_Composition.java`

## Concept
Composition — building complex objects out of other objects ("has-a" relationships) as an alternative to inheritance ("is-a"), including delegation and the classic Strategy Pattern example.

## Full Line-by-Line Breakdown

### `public class _13_Composition {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is Composition?
No executable code — just the conceptual framing. Composition models a **"has-a"** relationship (a vehicle **has** an engine), contrasted directly with inheritance's **"is-a"** relationship (a dog **is** an animal).

---

### SECTION 2: A Simple Composition Example

**`Engine v8Engine = new Engine("V8", 450);`**
Creates a standalone `Engine` object.

**`MyVehicle myVehicle = new MyVehicle("Mustang", v8Engine);`**
Creates a `MyVehicle` object, **passing the engine object in** — `MyVehicle` doesn't build its own engine internally; it receives one and holds a reference to it as a field.

**`myVehicle.start();`**
Calls `start()` on the vehicle — but internally, this method doesn't contain any actual engine-starting logic itself; it hands that responsibility off to the `Engine` object it holds (see Section 7: Delegation).

**`myVehicle.displayInfo();`**
Prints the vehicle's model along with details pulled directly from its contained `Engine` object.

---

### SECTION 3: Why Not Just Use Inheritance Here?
No executable code — a commented-out example (`class MyVehicle extends Engine { }`) showing what would be **conceptually wrong**: a vehicle is not a specialized *type* of engine, it merely *contains* one. Using `extends` here would create a nonsensical class hierarchy.

---

### SECTION 4: Composition Allows Swapping Parts At Runtime

**`Engine v6Engine = new Engine("V6", 300);`**
A second, different `Engine` object.

**`myVehicle.setEngine(v6Engine);`**
Replaces `myVehicle`'s engine entirely — the **same vehicle object**, now equipped with a completely different engine.

**`myVehicle.start();` / `myVehicle.displayInfo();`**
Both now reflect the new V6 engine's details, proving the swap actually took effect.

**Why this matters:** this kind of runtime flexibility is **impossible** with inheritance — you can never change what a class `extends` after it's compiled, but you absolutely can change what an object *has*, since it's just a field being reassigned.

---

### SECTION 5: Composition With Multiple Contained Objects

**`Engine hybridEngine = new Engine("Hybrid", 200);` / `GPS carGPS = new GPS("Garmin Pro");` / `SoundSystem soundSystem = new SoundSystem("Bose Premium");`**
Three independent objects, each representing a different component.

**`MyVehicle fullyLoadedVehicle = new MyVehicle("Tesla Model S", hybridEngine);`**
Creates a vehicle with just the engine set initially.

**`fullyLoadedVehicle.setGps(carGPS);` / `fullyLoadedVehicle.setSoundSystem(soundSystem);`**
Adds the other two components **after** creation, via setters — showing that a composed object doesn't need every "part" supplied all at once in the constructor.

**`fullyLoadedVehicle.start();` / `.useGps();` / `.playMusic();`**
Each call delegates to a different contained object — the engine, the GPS, and the sound system respectively — demonstrating that one class can be composed of **multiple** independent objects, each handling its own responsibility.

---

### SECTION 6: Composition vs Inheritance — The Duck Example

**The commented-out "bad design" example**
Shows the problem: if `Duck` had a `fly()` method and `RubberDuck extends Duck`, you'd be forced to override `fly()` to do nothing — technically valid Java, but conceptually dishonest, since the class hierarchy implies every duck can fly when that's clearly not true.

**`RealDuck realDuck = new RealDuck("Donald", new CanFly());`**
Creates a `RealDuck`, composed with a `CanFly` behavior object.

**`RubberDuck rubberDuck = new RubberDuck("Rubbert", new CannotFly());`**
Creates a `RubberDuck`, composed with a **different** behavior object — `CannotFly`.

**`realDuck.performFly();` / `rubberDuck.performFly();`**
Both call the same method name, but each produces different output — not because of method overriding (both `RealDuck` and `RubberDuck` share the exact same `performFly()` inherited from `Duck`), but because each duck was **composed** with a different behavior object at creation time.

---

### SECTION 7: Delegation
No new executable code — a pointer back to `MyVehicle.start()`, which doesn't implement engine-starting logic itself; it simply calls `engine.start()`, handing the actual work off to the contained object. This delegation is the actual mechanism that makes composition work in practice.

---

### SECTION 8: When To Use Composition vs Inheritance
No new code — a decision guide. Use inheritance for a genuine "is-a" relationship needing full identity/behavior sharing and polymorphism through a type hierarchy; use composition for "has-a" relationships, runtime part-swapping, or combining multiple independent capabilities without being limited to Java's single-inheritance rule.

---

### The `Engine`, `GPS`, and `SoundSystem` Classes

```java
class Engine {
    String type;
    int horsepower;

    Engine(String type, int horsepower) {
        this.type = type;
        this.horsepower = horsepower;
    }

    void start() {
        System.out.println(type + " engine starting... " + horsepower + " HP ready.");
    }
}
```
A standalone class with its own fields and behavior — it has no knowledge of `MyVehicle` at all; it's simply a self-contained object that happens to get **used** by `MyVehicle`.

`GPS` and `SoundSystem` follow the identical pattern — each a small, independent class with one field and one method, entirely unaware of the vehicle that will eventually contain them.

---

### The `MyVehicle` Class

```java
class MyVehicle {
    String model;
    Engine engine;
    GPS gps;
    SoundSystem soundSystem;

    MyVehicle(String model, Engine engine) {
        this.model = model;
        this.engine = engine;
    }

    void setEngine(Engine engine) {
        this.engine = engine;
    }

    void setGps(GPS gps) {
        this.gps = gps;
    }

    void setSoundSystem(SoundSystem soundSystem) {
        this.soundSystem = soundSystem;
    }

    void start() {
        System.out.println(model + " is starting...");
        engine.start();
    }

    void useGps() {
        if (gps != null) {
            gps.navigate();
        } else {
            System.out.println(model + " has no GPS installed.");
        }
    }

    void playMusic() {
        if (soundSystem != null) {
            soundSystem.play();
        } else {
            System.out.println(model + " has no sound system installed.");
        }
    }

    void displayInfo() {
        System.out.println(model + " is equipped with a " + engine.type +
                " engine (" + engine.horsepower + " HP)");
    }
}
```
Fields `engine`, `gps`, and `soundSystem` are all references to **other objects**, not primitive data — this is composition in its most direct form: `MyVehicle` doesn't `extend` any of these classes, it simply **holds references** to instances of them. `gps` and `soundSystem` are treated as optional (they can be `null`), so `useGps()` and `playMusic()` each check for `null` before attempting to use them, avoiding a crash if that component was never set.

---

### The `FlyBehavior` Interface and Implementations

```java
interface FlyBehavior {
    void fly();
}

class CanFly implements FlyBehavior {
    @Override
    public void fly() { System.out.println("Flying high in the sky!"); }
}

class CannotFly implements FlyBehavior {
    @Override
    public void fly() { System.out.println("Cannot fly - just floats or sits still."); }
}
```
A small interface with two interchangeable implementations — each representing a distinct **behavior** rather than a distinct "thing." This is the classic **Strategy Pattern**: instead of hardcoding one fixed behavior into a class (or being forced to override it away via inheritance), you compose in whichever behavior object actually fits.

---

### The `Duck` Abstract Class and Subclasses

```java
abstract class Duck {
    String name;
    FlyBehavior flyBehavior;

    Duck(String name, FlyBehavior flyBehavior) {
        this.name = name;
        this.flyBehavior = flyBehavior;
    }

    void performFly() {
        System.out.print(name + ": ");
        flyBehavior.fly();
    }
}

class RealDuck extends Duck {
    RealDuck(String name, FlyBehavior flyBehavior) {
        super(name, flyBehavior);
    }
}

class RubberDuck extends Duck {
    RubberDuck(String name, FlyBehavior flyBehavior) {
        super(name, flyBehavior);
    }
}
```
`Duck` holds a `FlyBehavior` field — composed in, not inherited — and its `performFly()` method **delegates** to whichever behavior object was supplied at construction. `RealDuck` and `RubberDuck` both extend `Duck` (a genuine "is-a" relationship — both really are ducks), but their **flying capability** is entirely determined by composition, not by which subclass they are. This is a deliberate combination of both patterns: inheritance for genuine shared identity, composition for interchangeable behavior.

## Key Rules / Gotchas Recap

- The **"is-a" test** decides the choice: if a subclass wouldn't genuinely be a specialized type of its parent, that's a strong signal to use composition instead
- Composition allows swapping parts at **runtime** (`myVehicle.setEngine(...)`) — something inheritance can never do once a class is compiled
- "Favor composition over inheritance" is a real, widely-cited OOP design principle — not just a rule for this exercise
- The Duck/FlyBehavior example is a genuine, commonly-used real-world design pattern (the Strategy Pattern) — composing in a behavior object rather than hardcoding or forcing an inherited one is an idea you'll see constantly in production codebases

## Why This Structure Exists

Composition solves problems inheritance cannot: it enables runtime flexibility (swapping parts), avoids dishonest class hierarchies (a `RubberDuck` that "can fly" but does nothing), and sidesteps Java's single-inheritance limit by letting one class combine as many independent objects as it needs. Understanding when to reach for composition instead of inheritance is one of the most practically useful design skills in all of OOP — arguably more consequential day-to-day than any single pillar on its own.