public class _13_Composition {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS COMPOSITION?
        // Building a class out of OTHER objects, rather than inheriting
        // from a parent class. This models a "HAS-A" relationship,
        // as opposed to inheritance's "IS-A" relationship.
        //
        // Example: A Vehicle HAS-A Engine (composition)
        //          vs. A Dog IS-A Animal (inheritance)
        // ============================================


        // ============================================
        // SECTION 2: A SIMPLE COMPOSITION EXAMPLE
        // MyVehicle doesn't extend Engine - it simply CONTAINS an Engine object
        // as one of its fields, and delegates work to it
        // ============================================

        Engine v8Engine = new Engine("V8", 450);
        MyVehicle myVehicle = new MyVehicle("Mustang", v8Engine);

        myVehicle.start();
        myVehicle.displayInfo();


        // ============================================
        // SECTION 3: WHY NOT JUST USE INHERITANCE HERE?
        // "MyVehicle extends Engine" would be WRONG - a vehicle is not a TYPE of
        // Engine, it merely CONTAINS one. Using inheritance for a
        // has-a relationship creates a confusing, incorrect class hierarchy.
        // ============================================

        // class MyVehicle extends Engine { }  // conceptually wrong - a vehicle IS-NOT-A Engine


        // ============================================
        // SECTION 4: COMPOSITION ALLOWS SWAPPING PARTS AT RUNTIME
        // Since the Engine is just a field, not baked into the class
        // hierarchy, you can freely swap it for a different one
        // ============================================

        Engine v6Engine = new Engine("V6", 300);
        myVehicle.setEngine(v6Engine);  // swap the engine entirely
        myVehicle.start();
        myVehicle.displayInfo();
        // This flexibility is IMPOSSIBLE with inheritance - you can't change
        // what a class "extends" at runtime, but you CAN change what it "has"


        // ============================================
        // SECTION 5: COMPOSITION WITH MULTIPLE CONTAINED OBJECTS
        // A class can be composed of MANY other objects, each handling
        // its own responsibility - this is a very common real-world pattern
        // ============================================

        Engine hybridEngine = new Engine("Hybrid", 200);
        GPS carGPS = new GPS("Garmin Pro");
        SoundSystem soundSystem = new SoundSystem("Bose Premium");

        MyVehicle fullyLoadedVehicle = new MyVehicle("Tesla Model S", hybridEngine);
        fullyLoadedVehicle.setGps(carGPS);
        fullyLoadedVehicle.setSoundSystem(soundSystem);

        fullyLoadedVehicle.start();
        fullyLoadedVehicle.useGps();
        fullyLoadedVehicle.playMusic();


        // ============================================
        // SECTION 6: COMPOSITION VS INHERITANCE - A CLASSIC EXAMPLE
        // "Favor composition over inheritance" is a well-known OOP principle.
        // Here's why: imagine trying to model a Duck using inheritance alone
        // ============================================

        // BAD DESIGN (using inheritance for behavior that varies):
        // class Duck { void fly() {...} }
        // class RubberDuck extends Duck { } // Uh oh - rubber ducks CAN'T fly!
        // You'd have to override fly() to do nothing, which is awkward and
        // misleading - the class hierarchy LIES about what a RubberDuck can do

        // GOOD DESIGN (using composition for interchangeable behavior):
        RealDuck realDuck = new RealDuck("Donald", new CanFly());
        RubberDuck rubberDuck = new RubberDuck("Rubbert", new CannotFly());

        realDuck.performFly();
        rubberDuck.performFly();
        // Each duck is COMPOSED with a specific flying BEHAVIOR object,
        // rather than inheriting a behavior that might not actually fit


        // ============================================
        // SECTION 7: DELEGATION - THE MECHANISM BEHIND COMPOSITION
        // Composition works by DELEGATING method calls to the contained
        // object, rather than implementing everything itself
        // ============================================

        // See MyVehicle.start() below - it doesn't implement engine-starting logic
        // itself, it DELEGATES that responsibility to engine.start()


        // ============================================
        // SECTION 8: WHEN TO USE COMPOSITION VS INHERITANCE
        // ============================================

        // Use INHERITANCE when:
        // - There's a genuine "is-a" relationship (a Dog IS-A Animal)
        // - The child truly shares the parent's entire identity and behavior set
        // - You want polymorphism through a shared type hierarchy

        // Use COMPOSITION when:
        // - There's a "has-a" relationship (a Vehicle HAS-A Engine)
        // - You need to swap out behavior/parts at runtime
        // - You want to combine multiple independent capabilities without
        //   being locked into a single inheritance chain (recall: Java only
        //   allows extending ONE class, but you can COMPOSE with as many
        //   objects as you want)
        // - The relationship doesn't hold up to the "is-a" test
    }
}


// ============================================
// COMPOSITION EXAMPLE: MyVehicle HAS-A Engine, GPS, SoundSystem
// ============================================

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

class GPS {
    String brand;

    GPS(String brand) {
        this.brand = brand;
    }

    void navigate() {
        System.out.println(brand + " GPS calculating route...");
    }
}

class SoundSystem {
    String brand;

    SoundSystem(String brand) {
        this.brand = brand;
    }

    void play() {
        System.out.println(brand + " sound system playing music.");
    }
}

class MyVehicle {
    String model;
    Engine engine;         // MyVehicle HAS-A Engine
    GPS gps;                // MyVehicle HAS-A GPS (optional, may be null)
    SoundSystem soundSystem; // MyVehicle HAS-A SoundSystem (optional, may be null)

    MyVehicle(String model, Engine engine) {
        this.model = model;
        this.engine = engine;
    }

    void setEngine(Engine engine) {
        this.engine = engine;  // swap the engine at runtime - only possible with composition
    }

    void setGps(GPS gps) {
        this.gps = gps;
    }

    void setSoundSystem(SoundSystem soundSystem) {
        this.soundSystem = soundSystem;
    }

    // DELEGATION: MyVehicle doesn't know HOW an engine starts, it just asks the
    // engine object to do it
    void start() {
        System.out.println(model + " is starting...");
        engine.start();  // delegates the actual work to the Engine object
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


// ============================================
// COMPOSITION VS INHERITANCE EXAMPLE: Duck Behavior
// Instead of inheriting a "fly" behavior that might not fit, each Duck
// is COMPOSED with a specific FlyBehavior object
// ============================================

interface FlyBehavior {
    void fly();
}

class CanFly implements FlyBehavior {
    @Override
    public void fly() {
        System.out.println("Flying high in the sky!");
    }
}

class CannotFly implements FlyBehavior {
    @Override
    public void fly() {
        System.out.println("Cannot fly - just floats or sits still.");
    }
}

abstract class Duck {
    String name;
    FlyBehavior flyBehavior;  // Duck HAS-A FlyBehavior, rather than inheriting one fixed version

    Duck(String name, FlyBehavior flyBehavior) {
        this.name = name;
        this.flyBehavior = flyBehavior;
    }

    void performFly() {
        System.out.print(name + ": ");
        flyBehavior.fly();  // delegates to whichever behavior object was composed in
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