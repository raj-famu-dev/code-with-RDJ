public class _6_Inheritance {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS INHERITANCE?
        // A mechanism where a CHILD class automatically gets the fields and
        // methods of a PARENT class, using the 'extends' keyword.
        // This is Java's primary tool for code reuse across related classes.
        // ============================================

        Animal genericAnimal = new Animal("Generic Animal");
        genericAnimal.eat();
        genericAnimal.sleep();


        // ============================================
        // SECTION 2: A CHILD CLASS INHERITING FROM A PARENT
        // Dog automatically gets eat() and sleep() from Animal -
        // we don't need to rewrite them
        // ============================================

        Dog dog = new Dog("Rex", "Labrador");
        dog.eat();       // inherited from Animal
        dog.sleep();     // inherited from Animal
        dog.bark();      // Dog's own additional method


        // ============================================
        // SECTION 3: THE 'super' KEYWORD - CALLING THE PARENT'S CONSTRUCTOR
        // A child class's constructor MUST call the parent's constructor
        // (explicitly with super(...), or implicitly if parent has a no-arg one)
        // super(...) MUST be the very first line if used explicitly
        // ============================================

        // See Dog's constructor below: super(name); initializes the inherited
        // 'name' field, which lives in the PARENT class


        // ============================================
        // SECTION 4: METHOD OVERRIDING
        // A child class can provide its OWN version of a method that already
        // exists in the parent - this REPLACES the parent's behavior when
        // called on a child object
        // ============================================

        Animal cat = new Cat("Whiskers");
        cat.makeSound();  // calls Cat's OVERRIDDEN version, not Animal's generic one

        Animal genericAnimal2 = new Animal("Unknown");
        genericAnimal2.makeSound();  // calls Animal's original version


        // ============================================
        // SECTION 5: @Override ANNOTATION
        // Not required, but STRONGLY recommended - tells the compiler
        // "I intend to override a parent method" - catches typos at compile time
        // ============================================

        // See Cat.makeSound() below - if you misspell the method name or
        // get the parameters wrong, @Override causes a compile ERROR instead
        // of silently creating an unrelated new method


        // ============================================
        // SECTION 6: USING 'super' TO CALL THE PARENT'S METHOD (NOT JUST CONSTRUCTOR)
        // Sometimes you want to EXTEND the parent's behavior, not fully replace it
        // ============================================

        Dog dog2 = new Dog("Buddy", "Beagle");
        dog2.makeSound();  // calls parent's version FIRST, then adds its own extra line


        // ============================================
        // SECTION 7: ACCESSING INHERITED FIELDS
        // Child classes can directly use parent fields, AS LONG AS the
        // access modifier allows it (private fields are NOT directly accessible -
        // covered properly in _10_AccessModifiers, but noted here)
        // ============================================

        System.out.println(dog.name + " is a " + dog.breed);
        // 'name' is inherited from Animal, 'breed' is Dog's own field


        // ============================================
        // SECTION 8: MULTI-LEVEL INHERITANCE
        // A class can inherit from a class that ITSELF inherits from another -
        // forms a chain: Grandparent -> Parent -> Child
        // ============================================

        Puppy puppy = new Puppy("Max", "Poodle", 2);
        puppy.eat();          // from Animal (grandparent)
        puppy.bark();         // from Dog (parent)
        puppy.playFetch();    // Puppy's own method
        System.out.println(puppy.name + " is " + puppy.ageInMonths + " months old");


        // ============================================
        // SECTION 9: JAVA DOES NOT ALLOW MULTIPLE CLASS INHERITANCE
        // A class can only extend ONE parent class directly
        // (this limitation is exactly why interfaces exist - covered in _9_Interfaces)
        // ============================================

        // class Impossible extends Dog, Cat { }  // COMPILE ERROR - not allowed in Java


        // ============================================
        // SECTION 10: EVERY CLASS IMPLICITLY EXTENDS Object
        // Even if you don't write 'extends' anything, every class in Java
        // automatically inherits from java.lang.Object (the root of all classes)
        // This is where default toString(), equals(), hashCode() come from
        // (we'll override these properly in _12_EqualsHashCodeToString.java)
        // ============================================

        System.out.println("Default toString() output: " + genericAnimal.toString());
        // prints something like: Animal@1b6d3586 (class name + memory address hash)
        // - this default is not very useful, which is exactly why we override it later
    }
}


// ============================================
// PARENT CLASS (also called: superclass, base class)
// ============================================

class Animal {

    String name;

    Animal(String name) {
        this.name = name;
        System.out.println("[Animal constructor called for " + name + "]");
    }

    void eat() {
        System.out.println(name + " is eating.");
    }

    void sleep() {
        System.out.println(name + " is sleeping.");
    }

    // A method designed to be overridden by child classes
    void makeSound() {
        System.out.println(name + " makes a generic animal sound.");
    }
}


// ============================================
// CHILD CLASS (also called: subclass, derived class)
// ============================================

class Dog extends Animal {

    String breed;  // Dog's own additional field, doesn't exist in Animal

    Dog(String name, String breed) {
        super(name);  // calls Animal's constructor - MUST be the first line
        this.breed = breed;
        System.out.println("[Dog constructor called for " + name + "]");
    }

    // Dog's own unique method - not in Animal at all
    void bark() {
        System.out.println(name + " says: Woof woof!");
    }

    // Overriding makeSound(), but EXTENDING rather than fully replacing parent behavior
    @Override
    void makeSound() {
        super.makeSound();  // calls Animal's original version first
        System.out.println(name + " (a dog) also barks: Woof!");
    }
}


// ============================================
// ANOTHER CHILD CLASS - fully replaces the parent's method instead of extending it
// ============================================

class Cat extends Animal {

    Cat(String name) {
        super(name);
    }

    @Override
    void makeSound() {
        // Completely replaces Animal's version - doesn't call super.makeSound() at all
        System.out.println(name + " says: Meow!");
    }
}


// ============================================
// MULTI-LEVEL INHERITANCE: Puppy extends Dog, which extends Animal
// Puppy inherits from BOTH Dog AND Animal, up the whole chain
// ============================================

class Puppy extends Dog {

    int ageInMonths;

    Puppy(String name, String breed, int ageInMonths) {
        super(name, breed);  // calls Dog's constructor, which calls Animal's constructor
        this.ageInMonths = ageInMonths;
        System.out.println("[Puppy constructor called for " + name + "]");
    }

    void playFetch() {
        System.out.println(name + " is playing fetch!");
    }
}