# `_1_ClassesAndObjects.java`

## Concept
Classes as blueprints, objects as actual instances created from them — the foundational shift from procedural code (`01-basics`) into object-oriented thinking.

## Full Line-by-Line Breakdown

### `public class _1_ClassesAndObjects {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is A Class?
No executable code here — just the conceptual framing. A class is a **blueprint**: it describes what fields (data) and methods (behavior) something should have, but it doesn't actually exist as a real "thing" until an object is created from it.

---

### SECTION 2: What Is An Object?

**`Car car1 = new Car();`**
The `new` keyword actually **allocates memory** and creates a real object based on the `Car` blueprint. `car1` is a variable holding a reference to that object.

**`Car car2 = new Car();`**
A **second**, completely separate object — even though it's built from the exact same `Car` class, `car2` is independent of `car1` in memory.

**`car1.brand = "Toyota"; car1.model = "Corolla"; car1.year = 2022;`**
Uses dot notation to set each field **on this specific object**. This only affects `car1` — it has no effect on `car2` or any other `Car` object.

**`car2.brand = "Honda"; car2.model = "Civic"; car2.year = 2023;`**
Sets completely different values on the **second** object.

**The two `println` lines**
Print each car's details, proving they hold entirely different data despite being built from the same class.

---

### SECTION 3: Calling Methods On Objects

**`car1.startEngine();`**
Calls the `startEngine()` method **on `car1` specifically** — this method (defined in the `Car` class below) sets `isRunning = true` and prints a message using `car1`'s own `brand`/`model` values.

**`car1.displayInfo();`**
Calls `displayInfo()` on `car1`, printing all of its current field values in one formatted line.

**`car2.startEngine();` / `car2.displayInfo();`**
Same two method calls, but on the **second, independent object** — proving each object runs its own copy of the behavior using its own data.

---

### SECTION 4: Fields Have Default Values If Not Set

**`Car car3 = new Car();`**
A third object is created, but **no fields are ever assigned** to it.

**`car3.brand`** → prints `null`
The default value for any object/reference type field (like `String`) when left unset.

**`car3.year`** → prints `0`
The default value for `int` fields.

**`car3.isRunning`** → prints `false`
The default value for `boolean` fields.

**Why this matters:** unlike local variables inside a method (which have no default and must be initialized before use — recap from `01-basics`), **object fields are automatically initialized** to a safe default the moment the object is created.

---

### SECTION 5: Multiple Objects, Same Class, Different State

**`Car[] garage = new Car[3];`**
An array that can hold 3 `Car` objects (recap of Arrays from `01-basics`, now storing objects instead of primitives).

**`garage[0] = car1; garage[1] = car2; garage[2] = car3;`**
Places the three previously-created car objects into the array by index.

**`for (Car car : garage) { car.displayInfo(); }`**
A for-each loop walking through the array, calling `displayInfo()` on each car in turn. This proves the core idea of OOP: one blueprint (`Car`), but three genuinely different real-world "things" built from it, each with their own current state.

---

### SECTION 6: Objects As Method Parameters

**`renameCar(car1, "Toyota", "Camry");`**
Calls a method, passing `car1` itself (not just its data) along with two new String values.

**Inside `renameCar`:**
```java
static void renameCar(Car car, String newBrand, String newModel) {
    car.brand = newBrand;
    car.model = newModel;
}
```
The parameter `car` receives a **copy of the reference** to `car1` — but that copied reference still points to the exact same object in memory. So when this method changes `car.brand` and `car.model`, it's actually modifying `car1`'s real fields.

**`System.out.println("Car 1 after rename: " + car1.brand + " " + car1.model);`**
Confirms this — `car1` now shows `"Toyota Camry"`, even though the modification technically happened inside a separate method. This is the same reference-behavior gotcha first seen with arrays in `_9_Methods.java`.

---

### The `Car` Class Definition (Below `main`)

**`class Car { ... }`**
Note this class is **not** marked `public` — only one class per file can be `public`, and it must match the filename. Since `_1_ClassesAndObjects` is already the public class, `Car` is declared without an access modifier (package-private), which is perfectly valid for a supporting class in the same file.

**Fields:**
```java
String brand;
String model;
int year;
boolean isRunning;
```
These represent the **state** — the data each individual `Car` object will hold. Every object gets its own independent copy of these four fields.

**`void startEngine() { isRunning = true; System.out.println(...); }`**
A method representing **behavior**. Notice it references `brand`, `model`, and `isRunning` directly (no object name needed) — inside a class's own methods, fields are accessed directly, since the method is already running "on behalf of" whichever object called it.

**`void stopEngine() { isRunning = false; System.out.println(...); }`**
The counterpart method — sets `isRunning` back to `false`.

**`void displayInfo() { System.out.println("Car Info -> Brand: " + brand + ...); }`**
Prints all four fields in one formatted line, using whatever values the calling object currently holds.

## Key Rules / Gotchas Recap

- Nothing exists in memory until `new` is called — the class alone is just a description, not a real object
- Each object has its own **independent** copies of fields; modifying one object's fields never affects another object of the same class
- Object fields get **default values** automatically (`null`, `0`, `false`) if never explicitly set — unlike local variables, which have no default at all
- Passing an object into a method passes a copy of its **reference**, not a copy of the object itself — so modifying the object's fields inside that method **does** persist outside it, exactly like arrays did in `01-basics`

## Why This Structure Exists

This is the fundamental mental shift from `01-basics` into OOP: everything before this point was primitives and static procedural code operating on data directly. From here forward, data (fields) and behavior (methods) are bundled together into objects — a class describes the shape, and `new` brings a real, independent instance of that shape into existence. Every later OOP concept (constructors, inheritance, polymorphism) builds directly on this idea.