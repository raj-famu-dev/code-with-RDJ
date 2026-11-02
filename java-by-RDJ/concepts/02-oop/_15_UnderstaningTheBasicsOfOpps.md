# `_15_UnderstaningTheBasicsOfOpps.java`

> Walkthrough drafted with Claude from your existing code. Check it against your own understanding and rewrite it in your own words.

## Concept
A small program that shows all four OOP pillars working together: **encapsulation**, **abstraction**, **inheritance**, and **polymorphism**.

## Full Line-by-Line Breakdown

### The abstract parent: `Animals`
```java
abstract class Animals {
    private String name;  private int age;  private String category;
```
- **Encapsulation:** the fields are `private`; the outside world uses getters (`getName`, `getAge`, `getCategory`).
- The constructor sets `name` and `category`, then calls `setAge(age)` so even construction goes through validation.
- **Validating setter:** `setAge` accepts `age > 0`; otherwise it prints `Invalid age for <name> - defaulting to 0.` and stores `0`.
- **Abstraction:** `abstract void makeSound();` has no body, so every subclass **must** supply its own sound. `Animals` does not know how each animal sounds.
- `breathe()` is a concrete method shared by every subclass, written once.
- `displayInfo()` prints the name, category, and age, then calls `makeSound()`. It does not know which sound will play. That is polymorphism happening inside the parent.

### The children: `Dogs` and `Cats`
```java
class Dogs extends Animals {
    Dogs(String name, int age) { super(name, age, "Canine"); }
    @Override void makeSound() { System.out.println(getName() + " says: Woof Woof!"); }
}
```
- **Inheritance:** `extends Animals` gives them the fields' accessors, `breathe()`, and `displayInfo()` for free.
- `super(name, age, "Canine")` calls the parent constructor.
- **Overriding:** each class implements `makeSound()` its own way. `Cats` does the same with `"Feline"` and `Meow!`.

### `main`: everything comes together
- `// Animals animal = new Animals(...)` is commented out: an abstract class cannot be instantiated.
- `new Dogs("Rex", -5)` triggers validation. Output: `Invalid age for Rex - defaulting to 0.` then `Rex's age after invalid input: 0`.
- `dog.breathe(); cat.breathe();` use the **same** inherited method: `Rex is breathing...`, `Wiskers is breathing...`.
- `Animals[] animals = {dog, cat};` is an array typed as the **abstract parent** holding different children.
- The loop calls `a.displayInfo()`; each object plays its own sound:
```
Rex (Canine, age 0): Rex says: Woof Woof!
Wiskers (Feline, age 3): Wiskers says: Meow!
```

## Things to check in your own code
- **`static void main()` and JDK 21.** A `main` with no `String[] args` and no `public` is a newer language feature. On a plain JDK 21, `java _15_UnderstaningTheBasicsOfOpps` fails with `Error: Main method not found` (this was tested). It runs with `--enable-preview` (compile with `--release 21 --enable-preview`), or on a later JDK where the feature is standard. Your README badge says Java 21, so the safest fix is `public static void main(String[] args)`.
- **`setAge` treats `0` as invalid** because of `age > 0`. A newborn animal with age `0` would print the "Invalid age" message. `age >= 0` is probably what you mean.
- **Class names** `Animals`, `Dogs`, `Cats` are plural; Java convention is singular (`Animal`, `Dog`, `Cat`). Also, top-level classes with common names in the default package can collide with a same-named class in another file of the same module.

## Key Rules / Gotchas Recap
- Abstract classes cannot be instantiated; they force subclasses to implement abstract methods
- Private fields plus a validating setter protect an object's state
- A parent-typed variable can hold any child and calls the child's overridden method at runtime

## Why This Structure Exists
This is the capstone of `02-oop`: instead of four separate demos, one small program needs all four pillars at once. That is closer to how real code is organized.
