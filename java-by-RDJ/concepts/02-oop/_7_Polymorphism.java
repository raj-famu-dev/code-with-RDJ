public class _7_Polymorphism {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS POLYMORPHISM?
        // "Many forms" - the same method call can behave differently
        // depending on WHICH object is actually being used.
        // Two types in Java: compile-time (overloading) and runtime (overriding)
        // ============================================


        // ============================================
        // SECTION 2: COMPILE-TIME POLYMORPHISM (RECAP FROM _9_Methods.java)
        // Method overloading - Java decides WHICH version to call based on
        // argument types/count, decided at COMPILE time, before the program runs
        // ============================================

        Calculator calc = new Calculator();
        System.out.println("add(int, int): " + calc.add(2, 3));
        System.out.println("add(double, double): " + calc.add(2.5, 3.5));
        System.out.println("add(int, int, int): " + calc.add(1, 2, 3));
        // Java picks the right version just by looking at the arguments - no
        // runtime decision needed, hence "compile-time" polymorphism


        // ============================================
        // SECTION 3: RUNTIME POLYMORPHISM (THE MAIN FOCUS OF THIS TOPIC)
        // Method overriding + a PARENT-TYPE reference pointing to a CHILD object.
        // Which method actually runs is decided at RUNTIME, based on the
        // ACTUAL object type, not the reference type.
        // ============================================

        PolyAnimal myAnimal;  // declared as PARENT type

        myAnimal = new PolyDog();   // but actually holds a CHILD object
        myAnimal.makeSound();       // runs PolyDog's version, NOT PolyAnimal's!

        myAnimal = new PolyCat();   // now holds a DIFFERENT child object
        myAnimal.makeSound();       // runs PolyCat's version instead

        // This is called UPCASTING - treating a child object as its parent type.
        // The reference type (PolyAnimal) determines what you're ALLOWED to call,
        // but the actual object type determines what ACTUALLY runs.


        // ============================================
        // SECTION 4: WHY THIS IS USEFUL - ONE METHOD, MANY BEHAVIORS
        // Instead of writing separate code for every animal type, you can
        // write ONE method that works with ANY PolyAnimal subtype
        // ============================================

        PolyAnimal[] animals = { new PolyDog(), new PolyCat(), new PolyAnimal() };

        System.out.println("Making all animals in the array make their sound:");
        for (PolyAnimal a : animals) {
            a.makeSound();  // each one calls ITS OWN overridden version automatically
        }
        // This loop never needed to know the SPECIFIC type of each animal -
        // it just trusts each one to know how to make its own sound correctly.
        // This is the real power of polymorphism: writing flexible, reusable code.


        // ============================================
        // SECTION 5: A PARENT REFERENCE CAN ONLY CALL METHODS THAT EXIST
        // IN THE PARENT CLASS - even if the actual object has MORE methods
        // ============================================

        PolyAnimal myDog = new PolyDog();
        myDog.makeSound();  // fine - makeSound() exists in PolyAnimal

        // myDog.fetch();  // COMPILE ERROR! Even though the actual object IS a PolyDog,
        // the reference TYPE is PolyAnimal, and PolyAnimal doesn't have a fetch() method.
        // The compiler only checks what the REFERENCE TYPE promises exists.


        // ============================================
        // SECTION 6: DOWNCASTING - GETTING BACK TO THE SPECIFIC CHILD TYPE
        // If you need to call a CHILD-only method, you must cast back down
        // ============================================

        PolyAnimal someAnimal = new PolyDog();  // upcast
        PolyDog actualDog = (PolyDog) someAnimal;  // downcast back to PolyDog
        actualDog.fetch();  // now this works - we have full PolyDog access again


        // ============================================
        // SECTION 7: THE instanceof OPERATOR
        // Safely check what type an object ACTUALLY is at runtime, before
        // attempting a downcast - prevents a ClassCastException crash
        // ============================================

        PolyAnimal mysteryAnimal = new PolyCat();

        // Modern Java (16+) pattern matching shorthand - combines the check
        // AND the cast into one line
        if (mysteryAnimal instanceof PolyCat catRef) {
            catRef.scratch();
            System.out.println("Pattern matching instanceof also works: " + catRef);
        }


        // ============================================
        // SECTION 8: THE DANGER OF DOWNCASTING WITHOUT CHECKING FIRST
        // ============================================

        PolyAnimal riskyAnimal = new PolyCat();
        try {
            PolyDog wrongCast = (PolyDog) riskyAnimal;  // PolyCat is NOT a PolyDog - this will crash!
        } catch (ClassCastException e) {
            System.out.println("Caught error: cannot cast a Cat to a Dog - " + e.getMessage());
        }
        // This is EXACTLY why instanceof checks exist - always verify before downcasting


        // ============================================
        // SECTION 9: POLYMORPHISM WITH METHOD PARAMETERS
        // A method can accept the PARENT type, and work correctly no matter
        // WHICH child object is actually passed in
        // ============================================

        introduceAnimal(new PolyDog());
        introduceAnimal(new PolyCat());
        introduceAnimal(new PolyAnimal());
    }

    // This method only needs to know about PolyAnimal - it works for ANY subtype
    static void introduceAnimal(PolyAnimal animal) {
        System.out.print("Introducing this animal: ");
        animal.makeSound();
    }
}


// ============================================
// SUPPORTING CLASSES
// ============================================

class Calculator {
    int add(int a, int b) {
        return a + b;
    }

    double add(double a, double b) {
        return a + b;
    }

    int add(int a, int b, int c) {
        return a + b + c;
    }
}

class PolyAnimal {
    void makeSound() {
        System.out.println("The animal makes a generic sound.");
    }
}

class PolyDog extends PolyAnimal {
    @Override
    void makeSound() {
        System.out.println("The dog barks: Woof!");
    }

    void fetch() {
        System.out.println("The dog fetches the ball.");
    }
}

class PolyCat extends PolyAnimal {
    @Override
    void makeSound() {
        System.out.println("The cat meows: Meow!");
    }

    void scratch() {
        System.out.println("The cat scratches the post.");
    }
}