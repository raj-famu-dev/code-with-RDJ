# `_8_AbstractClasses.java`

## Concept
Abstract classes — cannot be instantiated directly, mix "must implement" (abstract methods) with "already implemented, shared" (concrete methods). The first half of the fourth OOP pillar: Abstraction.

## Full Line-by-Line Breakdown

### `public class _8_AbstractClasses {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is An Abstract Class?
No executable code — just the conceptual framing, plus a commented-out line (`// Shape shape = new Shape();`) showing exactly what would fail: you can never directly instantiate an abstract class, even though it looks like a normal class otherwise.

---

### SECTION 2: Creating Concrete Subclasses

**`Circle circle = new Circle(5);`**
Creates a `Circle` object — a **concrete** (non-abstract) subclass of `Shape`.

**`Rectangle rectangle = new Rectangle(4, 6);`**
Creates a `Rectangle` object — another concrete subclass.

**`circle.calculateArea()` / `rectangle.calculateArea()`**
Each calls its **own** implementation of `calculateArea()` — `Circle` uses the circle-area formula, `Rectangle` uses width × height. Neither could exist without providing this method, since `Shape` declares it as abstract.

---

### SECTION 3: Abstract Methods
No new executable code — a pointer to `Shape.calculateArea()` below, which has **no body at all**, just a signature ending in a semicolon. This is what forces every concrete subclass to supply its own implementation.

---

### SECTION 4: Concrete Methods Inside An Abstract Class

**`circle.displayInfo();` / `rectangle.displayInfo();`**
Both call the **same** `displayInfo()` method, defined once in `Shape` and never repeated in `Circle` or `Rectangle`. Since it's a fully-implemented (concrete) method living in the abstract parent, every subclass gets it for free through inheritance.

---

### SECTION 5: Polymorphism With Abstract Classes

**`Shape[] shapes = { new Circle(3), new Rectangle(2, 5), new Triangle(4, 6) };`**
An array typed as the abstract `Shape`, holding three genuinely different concrete objects.

**`for (Shape s : shapes) { System.out.println(s.getName() + " area: " + s.calculateArea()); }`**
A single loop correctly calls each shape's own `calculateArea()` — this is the same polymorphism mechanic from `_7_Polymorphism.java`, but now built on an **abstract** foundation that *guarantees* every element in the array genuinely has a working `calculateArea()` method to call. Unlike a plain parent class, an abstract class enforces this at compile time — there's no way a `Shape` subtype could exist without implementing it.

---

### SECTION 6: Abstract Classes Can Have Constructors
No new executable code — a pointer to the three subclass constructors below, each calling `super(name)` to initialize the shared `name` field defined in `Shape`. Even though `Shape` itself can never be instantiated directly, its constructor still runs — just only ever indirectly, through a subclass's `super(...)` call.

---

### SECTION 7: Abstract Classes Can Have Fields Too

**`circle.name`**
Accesses the `name` field — defined in the abstract `Shape` class, not in `Circle` itself, yet fully accessible on the `circle` object because it was inherited and initialized via the constructor chain.

---

### SECTION 8: A Subclass That Doesn't Implement An Abstract Method
No executable code — two commented-out examples showing the two possible outcomes: a concrete subclass that forgets to implement `calculateArea()` is a **compile error**, but that same subclass could be made valid by *also* declaring itself `abstract` — at the cost of also becoming non-instantiable itself, just like `Shape`.

---

### SECTION 9: When To Use An Abstract Class
No new code — a decision guide summarizing when this pattern fits: shared implementation, forced method implementation, a genuine "is-a" relationship, and shared fields/constructors across a family of related classes.

---

### The `Shape` Abstract Class

```java
abstract class Shape {
    String name;

    Shape(String name) {
        this.name = name;
    }

    abstract double calculateArea();

    void displayInfo() {
        System.out.println(name + " has an area of " + calculateArea());
    }

    String getName() {
        return name;
    }
}
```

**`abstract class Shape`** — the `abstract` keyword on the class itself is what prevents `new Shape(...)` from ever being called directly.

**`Shape(String name) { this.name = name; }`** — a normal-looking constructor; it can only ever run via a subclass's `super(name)` call, never directly.

**`abstract double calculateArea();`** — no body, ends in a semicolon. This is an **abstract method**: it declares that every concrete subclass *must* provide this method, without specifying anything about how.

**`void displayInfo() { ... }`** — a fully-implemented, **concrete** method. Notice it calls `calculateArea()` internally — even though `Shape` itself has no implementation for that method, this still works correctly at runtime because whichever actual subclass object is calling `displayInfo()` will supply its own real `calculateArea()` implementation (the same polymorphic dispatch mechanic from the previous topic).

**`String getName() { return name; }`** — a simple getter, also concrete and shared automatically.

---

### The `Circle`, `Rectangle`, and `Triangle` Subclasses

```java
class Circle extends Shape {
    double radius;

    Circle(double radius) {
        super("Circle");
        this.radius = radius;
    }

    @Override
    double calculateArea() {
        return Math.PI * radius * radius;
    }
}
```
`super("Circle")` passes a fixed name string up to `Shape`'s constructor. `calculateArea()` is `@Override`-annotated and provides the actual circle-area formula (`π × r²`).

```java
class Rectangle extends Shape {
    double width;
    double height;

    Rectangle(double width, double height) {
        super("Rectangle");
        this.width = width;
        this.height = height;
    }

    @Override
    double calculateArea() {
        return width * height;
    }
}
```
Same pattern — `super("Rectangle")`, then its own two fields and area formula.

```java
class Triangle extends Shape {
    double base;
    double height;

    Triangle(double base, double height) {
        super("Triangle");
        this.base = base;
        this.height = height;
    }

    @Override
    double calculateArea() {
        return 0.5 * base * height;
    }
}
```
Same pattern again — proving all three subclasses follow an identical structural contract (name via `super`, own fields, own `calculateArea()` formula), which is exactly what the abstract parent guarantees.

## Key Rules / Gotchas Recap

- An abstract class can **never** be instantiated directly, even though it can have fields, constructors, and fully-implemented methods just like a normal class
- Every abstract method must eventually be implemented by some concrete class down the inheritance chain — enforced by the compiler, not just a convention
- A concrete method inside an abstract class (like `displayInfo()`) can safely call an abstract method (like `calculateArea()`) — the actual implementation used depends on whichever real subclass object is calling it at runtime
- If a subclass doesn't implement all inherited abstract methods, it too must be declared `abstract`, meaning it also can't be instantiated directly

## Why This Structure Exists

This is the first half of the fourth OOP pillar, Abstraction — a way to define a shared contract (every `Shape` must know how to calculate its own area) while still allowing genuinely shared, concrete behavior (`displayInfo()`, `getName()`) to live in one place rather than being duplicated across every subclass. The next topic, Interfaces, offers a related but more flexible way to achieve a similar goal, and directly contrasting the two is exactly what `_9_Interfaces.java` covers.