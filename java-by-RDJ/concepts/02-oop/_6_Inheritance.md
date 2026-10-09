# `_6_Inheritance.java`

## Concept
Inheritance — a child class reuses and extends a parent class's fields and methods via `extends`, including `super()`, method overriding, `@Override`, and multi-level inheritance chains.

## Full Line-by-Line Breakdown

### `public class _6_Inheritance {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is Inheritance?

**`Animal genericAnimal = new Animal("Generic Animal");`**
Creates a plain `Animal` object directly — the parent class on its own.

**`genericAnimal.eat();` / `genericAnimal.sleep();`**
Calls two methods defined directly in `Animal`.

---

### SECTION 2: A Child Class Inheriting From A Parent

**`Dog dog = new Dog("Rex", "Labrador");`**
Creates a `Dog` object — a **child class** of `Animal`.

**`dog.eat();` / `dog.sleep();`**
Calls methods that `Dog` never defined itself — these are **inherited** directly from `Animal`, available automatically without needing to be rewritten.

**`dog.bark();`**
Calls a method that only exists on `Dog` — proving the child class has its parent's capabilities **plus** its own additional ones.

---

### SECTION 3: The `super` Keyword — Calling The Parent's Constructor
No new executable code here — a pointer to `Dog`'s constructor below, where `super(name);` is the very first line, explicitly invoking `Animal`'s constructor to properly initialize the inherited `name` field.

---

### SECTION 4: Method Overriding

**`Animal cat = new Cat("Whiskers");`**
Notice the **reference type** is `Animal`, but the actual object is a `Cat` — this is legal because `Cat extends Animal`.

**`cat.makeSound();`**
Even though the reference type is `Animal`, this calls **`Cat`'s overridden version** of `makeSound()`, not `Animal`'s original — because Java resolves overridden methods based on the actual object type at runtime (a preview of the next topic, Polymorphism).

**`Animal genericAnimal2 = new Animal("Unknown"); genericAnimal2.makeSound();`**
A plain `Animal` object calling the same method name — this time, since there's no overriding involved, it runs `Animal`'s own original version.

---

### SECTION 5: `@Override` Annotation
No new executable code — a pointer to `Cat.makeSound()` below, where `@Override` is used specifically to let the compiler verify this method genuinely matches a method that exists in the parent class, catching typos or signature mismatches as compile errors rather than silently creating an unrelated new method.

---

### SECTION 6: Using `super` To Call The Parent's Method

**`Dog dog2 = new Dog("Buddy", "Beagle");`**
A new `Dog` object.

**`dog2.makeSound();`**
Calls `Dog`'s overridden `makeSound()` — but unlike `Cat`'s version, `Dog`'s implementation calls `super.makeSound();` **first** (running `Animal`'s original message), then adds its own extra line afterward. This demonstrates **extending** parent behavior rather than fully replacing it.

---

### SECTION 7: Accessing Inherited Fields

**`dog.name + " is a " + dog.breed`**
`name` is a field defined in `Animal` (the parent) — `Dog` never redeclares it, yet `dog.name` works directly, since it was inherited. `breed` is `Dog`'s own field, added on top of what it inherited.

---

### SECTION 8: Multi-Level Inheritance

**`Puppy puppy = new Puppy("Max", "Poodle", 2);`**
Creates a `Puppy` object — `Puppy extends Dog`, and `Dog extends Animal`, forming a three-level chain.

**`puppy.eat();`**
Inherited all the way from `Animal` (the "grandparent" in this chain) — `Puppy` never defined this itself, nor did `Dog`.

**`puppy.bark();`**
Inherited from `Dog` (the direct parent).

**`puppy.playFetch();`**
`Puppy`'s own unique method, existing at neither the `Dog` nor `Animal` level.

**`puppy.name + " is " + puppy.ageInMonths + " months old"`**
`name` inherited from `Animal` (two levels up), `ageInMonths` defined directly on `Puppy` itself.

---

### SECTION 9: Java Does Not Allow Multiple Class Inheritance
No executable code — just a commented-out example (`class Impossible extends Dog, Cat { }`) showing syntax that would be a compile error, since Java permits a class to `extends` only **one** parent directly.

---

### SECTION 10: Every Class Implicitly Extends `Object`

**`genericAnimal.toString()`**
Even though `Animal` never explicitly wrote a `toString()` method, calling it still works — because **every** class in Java automatically inherits from `java.lang.Object`, which provides a default `toString()` implementation. The output looks like `Animal@1b6d3586` — the class name plus a memory address hash — not very readable, which is exactly why overriding `toString()` (covered properly in `_12_EqualsHashCodeToString.java`) becomes valuable.

---

### The `Animal` Class (Parent/Superclass)

```java
class Animal {
    String name;

    Animal(String name) {
        this.name = name;
        System.out.println("[Animal constructor called for " + name + "]");
    }

    void eat() { System.out.println(name + " is eating."); }
    void sleep() { System.out.println(name + " is sleeping."); }
    void makeSound() { System.out.println(name + " makes a generic animal sound."); }
}
```
Defines one field (`name`) and three methods, all available to any class that extends it. The bracketed print statement in the constructor exists purely so you can watch the console and confirm exactly when this constructor runs relative to any child class constructors.

---

### The `Dog` Class (Child/Subclass)

```java
class Dog extends Animal {
    String breed;

    Dog(String name, String breed) {
        super(name);
        this.breed = breed;
        System.out.println("[Dog constructor called for " + name + "]");
    }

    void bark() { System.out.println(name + " says: Woof woof!"); }

    @Override
    void makeSound() {
        super.makeSound();
        System.out.println(name + " (a dog) also barks: Woof!");
    }
}
```
`extends Animal` establishes the inheritance relationship. `super(name);` **must** be the first line in the constructor — it hands `name` up to `Animal`'s constructor, which is responsible for actually initializing that field. `makeSound()` is overridden, but calls `super.makeSound();` first to preserve and build on top of the parent's original behavior rather than discarding it.

---

### The `Cat` Class (Another Child/Subclass)

```java
class Cat extends Animal {
    Cat(String name) { super(name); }

    @Override
    void makeSound() {
        System.out.println(name + " says: Meow!");
    }
}
```
Also extends `Animal`, but its `makeSound()` override **fully replaces** the parent's behavior — no `super.makeSound()` call at all. This is a direct contrast to `Dog`'s approach in the same file, showing both overriding strategies side by side.

---

### The `Puppy` Class (Multi-Level Inheritance)

```java
class Puppy extends Dog {
    int ageInMonths;

    Puppy(String name, String breed, int ageInMonths) {
        super(name, breed);
        this.ageInMonths = ageInMonths;
        System.out.println("[Puppy constructor called for " + name + "]");
    }

    void playFetch() { System.out.println(name + " is playing fetch!"); }
}
```
`extends Dog` (not `Animal` directly) — but since `Dog` itself extends `Animal`, `Puppy` transitively inherits from both. `super(name, breed);` calls `Dog`'s two-argument constructor, which in turn calls `Animal`'s constructor via its own `super(name);` — forming a chain of constructor calls that all run in sequence from grandparent down to child.

## Key Rules / Gotchas Recap

- `super(...)` must be the **very first line** in a child constructor if used explicitly — nothing can come before it
- `@Override` isn't required syntactically, but protects against typos silently creating an unrelated new method instead of genuinely overriding the parent's
- A child class can either **fully replace** a parent method (`Cat`) or **extend** it via `super.methodName()` (`Dog`) — both are valid, depending on what you need
- Java allows only **single class inheritance** — one `extends` only; this constraint is exactly why interfaces exist as a workaround
- Multi-level inheritance chains (`Puppy → Dog → Animal`) are fully supported — a child inherits from its entire ancestor chain, not just its immediate parent
- Every class implicitly extends `java.lang.Object`, which is where the default (not very useful) `toString()`, `equals()`, and `hashCode()` come from

## Why This Structure Exists

Inheritance is the second OOP pillar — it's how Java avoids duplicating code across related classes (`Dog` and `Cat` both get `eat()`/`sleep()` for free from `Animal`), and it sets up the exact mechanism (`super`, method overriding) that Polymorphism — the very next topic — depends on entirely.