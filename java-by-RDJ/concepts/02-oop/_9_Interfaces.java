public class _9_Interfaces {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS AN INTERFACE?
        // A pure CONTRACT - it defines WHAT methods a class must have,
        // without (traditionally) providing any implementation at all.
        // A class "implements" an interface using the 'implements' keyword.
        // ============================================

        // Interface interface = new Interface();  // COMPILE ERROR - like abstract
        // classes, interfaces can NEVER be instantiated directly


        // ============================================
        // SECTION 2: A CLASS IMPLEMENTING AN INTERFACE
        // The class MUST provide a real implementation for every method
        // declared in the interface, or the class itself must be abstract
        // ============================================

        Sedan sedan = new Sedan();
        sedan.startEngine();
        sedan.stopEngine();


        // ============================================
        // SECTION 3: A CLASS CAN IMPLEMENT MULTIPLE INTERFACES
        // This is Java's actual workaround for not allowing multiple CLASS
        // inheritance - a class can only extend ONE class, but can implement
        // AS MANY interfaces as needed
        // ============================================

        AirCar airCar = new AirCar();
        airCar.startEngine();  // from Drivable
        airCar.stopEngine();   // from Drivable
        airCar.fly();          // from Flyable
        airCar.land();         // from Flyable
        // AirCar fulfills BOTH contracts at once - impossible with class
        // inheritance alone, since Java doesn't allow "extends A, B"


        // ============================================
        // SECTION 4: POLYMORPHISM WITH INTERFACES
        // Just like abstract classes, an interface TYPE can reference any
        // object that implements it - enabling the same flexible, reusable code
        // ============================================

        Drivable[] vehicles = { new Sedan(), new AirCar(), new Motorbike() };

        System.out.println("Starting all drivable vehicles:");
        for (Drivable v : vehicles) {
            v.startEngine();  // each one runs its OWN implementation
        }


        // ============================================
        // SECTION 5: DEFAULT METHODS (MODERN JAVA, 8+)
        // Interfaces CAN now provide actual implementation using 'default' -
        // implementing classes get this behavior FOR FREE, but can still
        // override it if they need different behavior
        // ============================================

        sedan.honk();    // uses Drivable's default implementation, unmodified
        airCar.honk();   // uses Drivable's default implementation too

        Motorbike motorbike = new Motorbike();
        motorbike.honk();   // Motorbike OVERRIDES the default honk() with its own version


        // ============================================
        // SECTION 6: STATIC METHODS IN INTERFACES (MODERN JAVA, 8+)
        // Utility-style methods that belong to the INTERFACE itself,
        // called directly on the interface name - not on any implementing object
        // ============================================

        Drivable.printDrivingRules();  // called on the interface itself, like a static class method


        // ============================================
        // SECTION 7: INTERFACE CONSTANTS
        // Any field declared in an interface is AUTOMATICALLY public, static,
        // and final - whether you write those keywords or not
        // ============================================

        System.out.println("Max speed limit constant: " + Drivable.MAX_SPEED_LIMIT);
        // Drivable.MAX_SPEED_LIMIT = 200;  // COMPILE ERROR - implicitly final, can't reassign


        // ============================================
        // SECTION 8: INTERFACE VS ABSTRACT CLASS - KEY DIFFERENCES
        // ============================================

        // Abstract class: can have constructors, instance fields with any
        //   access level, and a class can only extend ONE abstract class
        // Interface: (traditionally) no constructors, fields are always
        //   public static final constants, and a class can implement MANY interfaces

        // Modern Java has blurred some lines (default/static methods add real
        // behavior to interfaces now), but the MULTIPLE IMPLEMENTATION
        // capability remains the single biggest practical difference


        // ============================================
        // SECTION 9: instanceof WORKS WITH INTERFACES TOO
        // ============================================

        Drivable someVehicle = new AirCar();
        if (someVehicle instanceof Flyable) {
            Flyable flying = (Flyable) someVehicle;
            flying.fly();
            System.out.println("Confirmed: this drivable vehicle can ALSO fly.");
        }


        // ============================================
        // SECTION 10: WHEN TO USE AN INTERFACE VS ABSTRACT CLASS
        // ============================================

        // Use an INTERFACE when:
        // - Unrelated classes need to share a CAPABILITY, not a common identity
        //   (e.g., both a Bird and an Airplane can "fly", but they aren't related otherwise)
        // - A class might need MULTIPLE unrelated contracts fulfilled at once
        // - You're defining a pure behavioral contract with no shared state

        // Use an ABSTRACT CLASS when:
        // - Classes share a genuine "is-a" relationship AND common state/fields
        // - You want to share actual field data and constructors, not just method contracts
    }
}


// ============================================
// INTERFACE DEFINITIONS
// ============================================

interface Drivable {

    // Interface constant - implicitly public static final
    int MAX_SPEED_LIMIT = 120;

    // Abstract method - no body, every implementing class MUST provide one
    void startEngine();
    void stopEngine();

    // Default method - HAS a body, implementing classes get this for FREE
    // but can override it if they want different behavior
    default void honk() {
        System.out.println("Beep beep! (default horn sound)");
    }

    // Static method - belongs to the interface itself, called via interface name
    static void printDrivingRules() {
        System.out.println("Drive safely. Max speed limit: " + MAX_SPEED_LIMIT);
    }
}

interface Flyable {
    void fly();
    void land();
}


// ============================================
// CLASSES IMPLEMENTING THE INTERFACES
// ============================================

class Sedan implements Drivable {
    @Override
    public void startEngine() {
        System.out.println("Sedan engine started.");
    }

    @Override
    public void stopEngine() {
        System.out.println("Sedan engine stopped.");
    }
    // honk() not overridden - uses Drivable's default implementation automatically
}

class Motorbike implements Drivable {
    @Override
    public void startEngine() {
        System.out.println("Motorbike engine started.");
    }

    @Override
    public void stopEngine() {
        System.out.println("Motorbike engine stopped.");
    }

    // OVERRIDING the default method with motorbike-specific behavior
    @Override
    public void honk() {
        System.out.println("Beep! (a much smaller horn sound)");
    }
}

// A class implementing TWO interfaces at once - impossible with class inheritance alone
class AirCar implements Drivable, Flyable {
    @Override
    public void startEngine() {
        System.out.println("AirCar engine started.");
    }

    @Override
    public void stopEngine() {
        System.out.println("AirCar engine stopped.");
    }

    @Override
    public void fly() {
        System.out.println("AirCar is now airborne!");
    }

    @Override
    public void land() {
        System.out.println("AirCar has landed.");
    }
}