public class _10_AccessModifiers {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THE FOUR ACCESS MODIFIERS IN JAVA
        // Control WHO can see/use a class, field, method, or constructor
        //
        // 1. public     - accessible from ANYWHERE
        // 2. protected  - accessible within same package + subclasses (even in other packages)
        // 3. (default)  - accessible ONLY within the same package (no keyword written at all)
        // 4. private    - accessible ONLY within the same class
        // ============================================


        // ============================================
        // SECTION 2: private - MOST RESTRICTIVE
        // Only visible inside the SAME class - not even a subclass can access it directly
        // ============================================

        Vehicle vehicle = new Vehicle();
        vehicle.displayDetails();  // fine - public method

        // vehicle.serialNumber = "12345";  // COMPILE ERROR - serialNumber is private!
        // Must go through a public getter/setter instead (recap from Encapsulation)
        System.out.println("Serial number via getter: " + vehicle.getSerialNumber());


        // ============================================
        // SECTION 3: public - LEAST RESTRICTIVE
        // Accessible from ANY class, in ANY package, no restrictions at all
        // ============================================

        System.out.println("Public field directly accessible: " + vehicle.brand);
        vehicle.honk();  // public method, callable from anywhere


        // ============================================
        // SECTION 4: default (PACKAGE-PRIVATE) - NO KEYWORD WRITTEN
        // Accessible only to OTHER classes in the SAME package.
        // Since everything in this file has no package statement, they're
        // all technically in the same "default package" together, so this
        // WILL work here - but would FAIL if accessed from a class in a
        // different, named package.
        // ============================================

        vehicle.performMaintenance();  // default-access method - works here since
        // this main() method is in the same (default) package as Vehicle

        System.out.println("Default field: " + vehicle.modelYear);


        // ============================================
        // SECTION 5: protected - INTERMEDIATE RESTRICTION
        // Accessible within the same package (just like default), PLUS
        // accessible to SUBCLASSES even if they're in a DIFFERENT package
        // ============================================

        Truck truck = new Truck();
        truck.displayDetails();       // inherited public method
        truck.performMaintenance();   // inherited default method (works, same package)
        truck.showProtectedInfo();    // Truck's own method, which internally uses
        // the inherited protected field - demonstrating subclass access


        // ============================================
        // SECTION 6: ACCESS MODIFIERS ON CLASSES THEMSELVES
        // A top-level class can ONLY be public or default (package-private) -
        // NOT private or protected (those only apply to members INSIDE a class)
        // ============================================

        // public class SomeClass { }     // fine - accessible everywhere
        // class SomeClass { }             // fine - default, only this package
        // private class SomeClass { }     // COMPILE ERROR - not allowed at top level
        // protected class SomeClass { }   // COMPILE ERROR - not allowed at top level


        // ============================================
        // SECTION 7: SUMMARY TABLE (READ AS COMMENTS - CONCEPTUAL REFERENCE)
        // ============================================

        // Modifier      | Same Class | Same Package | Subclass (diff package) | Everywhere
        // -------------------------------------------------------------------------------
        // private       |     YES    |      NO      |           NO             |     NO
        // (default)     |     YES    |      YES     |           NO             |     NO
        // protected     |     YES    |      YES     |           YES            |     NO
        // public        |     YES    |      YES     |           YES            |     YES


        // ============================================
        // SECTION 8: WHY THIS MATTERS - REAL-WORLD REASONING
        // ============================================

        // - private: enforces encapsulation, protects internal implementation details
        // - default: useful for classes/helpers meant only for internal use within
        //   a specific package (like internal utility classes not meant for public API)
        // - protected: lets you share implementation details with subclasses
        //   (even across packages) while still hiding them from unrelated code
        // - public: your actual API - the parts of your code meant to be used
        //   by anyone, anywhere


        // ============================================
        // SECTION 9: TO TRULY TEST protected AND default ACROSS PACKAGES
        // ============================================

        // This single file can't fully demonstrate cross-package behavior,
        // since everything here shares the same (default) package.
        // To see it for real:
        //   1. Create a new package, e.g. concepts.oop.otherpackage
        //   2. Put a class there that tries to extend Vehicle and access
        //      its protected field - this WORKS
        //   3. Try accessing Vehicle's default-access field from that same
        //      external class (NOT via inheritance) - this FAILS to compile
        // This proves protected extends across packages via inheritance,
        // while default strictly does not, regardless of inheritance.
    }
}


// ============================================
// CLASS DEMONSTRATING ALL FOUR ACCESS LEVELS
// ============================================

class Vehicle {

    // --- PUBLIC: accessible from anywhere ---
    public String brand = "Generic Brand";

    // --- PRIVATE: only accessible within THIS class ---
    private String serialNumber = "SN-000000";

    // --- DEFAULT (no keyword): accessible only within the same package ---
    int modelYear = 2024;

    // --- PROTECTED: accessible in same package + any subclass, even in other packages ---
    protected String engineType = "Standard Engine";

    // --- PUBLIC METHOD ---
    public void displayDetails() {
        System.out.println("Brand: " + brand + ", Serial: " + serialNumber);
    }

    // --- PUBLIC GETTER for the private field (proper encapsulation) ---
    public String getSerialNumber() {
        return serialNumber;
    }

    // --- PUBLIC METHOD ---
    public void honk() {
        System.out.println(brand + " honks!");
    }

    // --- DEFAULT METHOD (package-private): no modifier written at all ---
    void performMaintenance() {
        System.out.println(brand + " (model year " + modelYear + ") is being serviced.");
    }
}


// ============================================
// SUBCLASS DEMONSTRATING protected ACCESS
// ============================================

class Truck extends Vehicle {

    void showProtectedInfo() {
        // 'engineType' is protected in Vehicle - Truck CAN access it directly
        // because Truck is a SUBCLASS, even though it's technically defined
        // in the same file/package here (the key guarantee protected gives
        // is that this would STILL work even if Truck were in a totally
        // different package from Vehicle)
        System.out.println("Engine type (inherited protected field): " + engineType);
    }
}