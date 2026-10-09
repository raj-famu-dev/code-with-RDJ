public class _1_ClassesAndObjects {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS A CLASS?
        // A class is a BLUEPRINT/TEMPLATE that defines what properties (fields)
        // and behaviors (methods) something should have.
        // It doesn't DO anything by itself - it just describes the shape.
        // ============================================

        // The Car class is defined below in this same file (outside main)


        // ============================================
        // SECTION 2: WHAT IS AN OBJECT?
        // An object is an actual INSTANCE created from a class -
        // real memory allocated, with its own actual values.
        // One class can produce many different objects, each independent.
        // ============================================

        Car car1 = new Car();  // 'new' creates an actual object in memory
        Car car2 = new Car();  // a completely separate, independent object

        car1.brand = "Toyota";
        car1.model = "Corolla";
        car1.year = 2022;

        car2.brand = "Honda";
        car2.model = "Civic";
        car2.year = 2023;

        System.out.println("Car 1: " + car1.brand + " " + car1.model + " (" + car1.year + ")");
        System.out.println("Car 2: " + car2.brand + " " + car2.model + " (" + car2.year + ")");
        // Proves car1 and car2 are independent - changing one never affects the other


        // ============================================
        // SECTION 3: CALLING METHODS ON OBJECTS
        // Methods defined in a class represent BEHAVIOR the object can perform
        // ============================================

        car1.startEngine();
        car1.displayInfo();

        car2.startEngine();
        car2.displayInfo();


        // ============================================
        // SECTION 4: FIELDS HAVE DEFAULT VALUES IF NOT SET
        // Unlike local variables (which need initialization), object fields
        // automatically get default values when the object is created
        // ============================================

        Car car3 = new Car();
        System.out.println("Unset car3 brand: " + car3.brand);   // null (default for objects/Strings)
        System.out.println("Unset car3 year: " + car3.year);     // 0 (default for int)
        System.out.println("Unset car3 isRunning: " + car3.isRunning);  // false (default for boolean)


        // ============================================
        // SECTION 5: MULTIPLE OBJECTS, SAME CLASS, DIFFERENT STATE
        // This is the whole point of OOP - one blueprint, many independent
        // real-world "things" built from it, each with their own current state
        // ============================================

        Car[] garage = new Car[3];
        garage[0] = car1;
        garage[1] = car2;
        garage[2] = car3;

        System.out.println("All cars in garage:");
        for (Car car : garage) {
            car.displayInfo();
        }


        // ============================================
        // SECTION 6: OBJECTS AS METHOD PARAMETERS
        // You can pass objects into methods, just like primitives -
        // but remember: it's the REFERENCE being passed, so changes to the
        // object's fields inside the method DO persist outside (unlike primitives)
        // ============================================

        renameCar(car1, "Toyota", "Camry");
        System.out.println("Car 1 after rename: " + car1.brand + " " + car1.model);
    }

    // Helper method demonstrating an object passed as a parameter
    static void renameCar(Car car, String newBrand, String newModel) {
        car.brand = newBrand;
        car.model = newModel;
    }
}


// ============================================
// THE CLASS DEFINITION ITSELF
// Notice: this is a SEPARATE class in the same file (not public, so only
// one file can have multiple classes as long as only ONE is public)
// ============================================

class Car {

    // --- FIELDS (also called instance variables or attributes) ---
    // These represent the STATE/DATA each object will hold
    String brand;
    String model;
    int year;
    boolean isRunning;  // defaults to false

    // --- METHODS ---
    // These represent BEHAVIOR - what an object of this class can DO

    void startEngine() {
        isRunning = true;
        System.out.println(brand + " " + model + "'s engine has started.");
    }

    void stopEngine() {
        isRunning = false;
        System.out.println(brand + " " + model + "'s engine has stopped.");
    }

    void displayInfo() {
        System.out.println("Car Info -> Brand: " + brand + ", Model: " + model +
                ", Year: " + year + ", Running: " + isRunning);
    }
}