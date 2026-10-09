# `_7_Polymorphism.java`

## Concept
Polymorphism — one reference type, many implementations. A parent-type reference can hold different child-type objects, each responding differently to the same method call. Covers both compile-time (overloading) and runtime (overriding) polymorphism, upcasting, downcasting, and `instanceof`.

## Full Line-by-Line Breakdown

### `public class _7_Polymorphism {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is Polymorphism?
No executable code — just the conceptual framing. "Many forms" — the same method call behaves differently depending on which object is actually being used. Two distinct types exist in Java: compile-time (resolved before the program runs) and runtime (resolved while the program runs).

---

### SECTION 2: Compile-Time Polymorphism (Recap)

**`Calculator calc = new Calculator();`**
Creates a `Calculator` object.

**`calc.add(2, 3)`**
Java matches this call to the `add(int, int)` overload based purely on the argument types.

**`calc.add(2.5, 3.5)`**
Matches `add(double, double)` instead.

**`calc.add(1, 2, 3)`**
Matches `add(int, int, int)` — three arguments.

**Why "compile-time":** the compiler determines exactly which method version to call just by inspecting the arguments in the source code — no runtime decision is involved at all. Recap of the overloading principle from `_9_Methods.java`.

---

### SECTION 3: Runtime Polymorphism (Main Focus)

**`PolyAnimal myAnimal;`**
Declares a variable with the **parent** type — at this point it holds no object yet.

**`myAnimal = new PolyDog();`**
Assigns a **child**-type object (`PolyDog`) to a parent-type reference (`PolyAnimal`). This is called **upcasting** — treating a child object as if it were its parent type.

**`myAnimal.makeSound();`**
Even though `myAnimal`'s declared type is `PolyAnimal`, this call runs `PolyDog`'s **overridden** version of `makeSound()`, not `PolyAnimal`'s original. This is the core of runtime polymorphism: which method body actually executes is determined by the object's **actual** type, not the reference's declared type.

**`myAnimal = new PolyCat();`**
Reassigns the same variable to hold a different child object entirely.

**`myAnimal.makeSound();`**
Now runs `PolyCat`'s version instead — same variable, same method call syntax, different behavior, because the underlying object changed.

---

### SECTION 4: Why This Is Useful

**`PolyAnimal[] animals = { new PolyDog(), new PolyCat(), new PolyAnimal() };`**
An array declared to hold `PolyAnimal` type — but actually containing three genuinely different object types, all valid since `PolyDog` and `PolyCat` both extend `PolyAnimal`.

**`for (PolyAnimal a : animals) { a.makeSound(); }`**
A single loop, written once, that correctly calls the right overridden version of `makeSound()` for **every** element — a `PolyDog` barks, a `PolyCat` meows, and a plain `PolyAnimal` makes its generic sound. The loop itself never needed to know each element's specific type — it simply trusts each object to know how to behave correctly. This is the real payoff of polymorphism: writing flexible code that works correctly across an entire family of related types without special-casing each one.

---

### SECTION 5: A Parent Reference Can Only Call Parent Methods

**`PolyAnimal myDog = new PolyDog();`**
Upcasting again — a `PolyDog` object stored in a `PolyAnimal`-typed variable.

**`myDog.makeSound();`**
Works fine — `makeSound()` exists in `PolyAnimal`, so the reference type permits calling it (even though the actual overridden version runs).

**The commented-out `myDog.fetch();`**
Would be a **compile error** if uncommented. Even though the actual object stored in `myDog` genuinely is a `PolyDog` (which does have a `fetch()` method), the **reference type** is `PolyAnimal`, and `PolyAnimal` has no `fetch()` method at all. The compiler only ever checks what the **declared reference type** promises exists — it doesn't look at the actual object underneath.

---

### SECTION 6: Downcasting

**`PolyAnimal someAnimal = new PolyDog();`**
Upcast, same as before.

**`PolyDog actualDog = (PolyDog) someAnimal;`**
A **downcast** — explicitly converting the reference back down to the more specific `PolyDog` type, using cast syntax `(PolyDog)`.

**`actualDog.fetch();`**
Now works, because `actualDog`'s declared type is genuinely `PolyDog` again, giving full access to `PolyDog`-specific methods.

---

### SECTION 7: The `instanceof` Operator

**`PolyAnimal mysteryAnimal = new PolyCat();`**
An object whose specific type isn't obvious just from the variable's declared type.

**`if (mysteryAnimal instanceof PolyCat catRef) { catRef.scratch(); ... }`**
The **modern pattern-matching** form of `instanceof` (Java 16+): this single line both **checks** whether `mysteryAnimal` is actually a `PolyCat`, **and**, if true, automatically creates a new variable `catRef` already cast to that type — combining the check and the cast in one step, safely.

**Why this matters:** checking `instanceof` **before** attempting a downcast is what prevents a runtime crash — see Section 8 for what happens without this safety check.

---

### SECTION 8: The Danger Of Downcasting Without Checking

**`PolyAnimal riskyAnimal = new PolyCat();`**
An object that is genuinely a `PolyCat`.

**`try { PolyDog wrongCast = (PolyDog) riskyAnimal; } catch (ClassCastException e) { ... }`**
Attempts to downcast a `PolyCat` object into `PolyDog` — an invalid cast, since a `PolyCat` is not a type of `PolyDog`. This compiles just fine (the compiler can't always know in advance that this specific cast will fail), but **crashes at runtime** with a `ClassCastException`, caught here and handled gracefully instead of crashing the whole program (a preview of proper exception handling, covered fully in `04-exceptions`).

**Why this exists:** to directly demonstrate the exact failure mode that `instanceof` checks (Section 7) are designed to prevent.

---

### SECTION 9: Polymorphism With Method Parameters

**`introduceAnimal(new PolyDog());` / `introduceAnimal(new PolyCat());` / `introduceAnimal(new PolyAnimal());`**
Calls the same method three times, passing three different object types.

**Inside `introduceAnimal`:**
```java
static void introduceAnimal(PolyAnimal animal) {
    System.out.print("Introducing this animal: ");
    animal.makeSound();
}
```
The method's parameter type is `PolyAnimal` — but since any subtype can be passed wherever a parent type is expected, this one method correctly handles all three calls, each producing the correct overridden sound.

---

### The `Calculator` Class

```java
class Calculator {
    int add(int a, int b) { return a + b; }
    double add(double a, double b) { return a + b; }
    int add(int a, int b, int c) { return a + b + c; }
}
```
Three overloaded versions of `add`, differentiated by parameter count/type — this is what Section 2 demonstrates.

---

### The `PolyAnimal` / `PolyDog` / `PolyCat` Classes

```java
class PolyAnimal {
    void makeSound() { System.out.println("The animal makes a generic sound."); }
}

class PolyDog extends PolyAnimal {
    @Override
    void makeSound() { System.out.println("The dog barks: Woof!"); }
    void fetch() { System.out.println("The dog fetches the ball."); }
}

class PolyCat extends PolyAnimal {
    @Override
    void makeSound() { System.out.println("The cat meows: Meow!"); }
    void scratch() { System.out.println("The cat scratches the post."); }
}
```
Note these are named with a `Poly` prefix specifically to avoid colliding with the identically-structured `Animal`/`Dog`/`Cat` classes already defined in `_6_Inheritance.java` — since this project doesn't use `package` statements, every class name must stay unique across the whole codebase. Structurally, this is the exact same parent/child relationship as `_6_Inheritance.java`, reused here specifically to demonstrate polymorphism on top of already-familiar inheritance.

## Key Rules / Gotchas Recap

- The **reference type** controls what methods are callable at compile time; the **actual object type** controls which overridden version actually runs at runtime
- Upcasting (child → parent reference) is always safe and often implicit; downcasting (parent → child reference) requires an explicit cast and carries real risk
- Always `instanceof`-check before downcasting — an invalid downcast compiles fine but throws a `ClassCastException` at runtime
- The real power of polymorphism is writing one piece of code (a loop, a method parameter) that correctly handles an entire family of related types without needing to know each one's specific identity

## Why This Structure Exists

This is the third OOP pillar, and arguably the one that makes OOP genuinely powerful rather than just an organizational convenience — it's what lets you write code against an abstraction (`PolyAnimal`) instead of hardcoding behavior for every concrete type individually. Every concept from `_6_Inheritance.java` (method overriding, `super`, the parent-child relationship) exists specifically to make this possible.