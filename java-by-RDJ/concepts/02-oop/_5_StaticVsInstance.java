public class _5_StaticVsInstance {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: INSTANCE MEMBERS (RECAP)
        // Belong to EACH object separately - every object gets its own copy
        // ============================================

        Employee emp1 = new Employee("Alice", 50000);
        Employee emp2 = new Employee("Bob", 60000);

        System.out.println(emp1.name + "'s salary: " + emp1.salary);
        System.out.println(emp2.name + "'s salary: " + emp2.salary);
        // Each object has its OWN independent name/salary - proven already in _1


        // ============================================
        // SECTION 2: STATIC FIELDS
        // Belong to the CLASS itself - shared across ALL objects.
        // There's only ONE copy in memory, no matter how many objects exist.
        // ============================================

        System.out.println("Company name (static): " + Employee.companyName);
        // Notice: accessed via the CLASS name, not an object - because it doesn't
        // belong to any single object

        // Changing it through the class affects what EVERY object "sees"
        Employee.companyName = "TechCorp International";
        System.out.println("emp1 sees company as: " + emp1.companyName);
        System.out.println("emp2 sees company as: " + emp2.companyName);
        // Both changed! Because there's only ONE shared copy, not one per object


        // ============================================
        // SECTION 3: STATIC FIELDS FOR TRACKING/COUNTING ACROSS OBJECTS
        // A very common real use case - since static fields persist and are
        // shared, they're perfect for counting how many objects have been made
        // ============================================

        System.out.println("Employees created so far: " + Employee.employeeCount);

        Employee emp3 = new Employee("Charlie", 55000);
        Employee emp4 = new Employee("Dana", 58000);

        System.out.println("Employees created now: " + Employee.employeeCount);
        // Increases each time - the constructor increments this shared counter


        // ============================================
        // SECTION 4: STATIC METHODS
        // Belong to the class, not any object. Called using the CLASS name.
        // Can ONLY directly access other static members (no 'this', no instance fields)
        // ============================================

        Employee.printCompanyInfo();  // called via class name, no object needed

        // This would NOT compile if attempted inside printCompanyInfo():
        // System.out.println(name);  // ERROR - 'name' is an instance field,
        // and static methods don't know WHICH object's name to use


        // ============================================
        // SECTION 5: INSTANCE METHODS CAN ACCESS BOTH STATIC AND INSTANCE MEMBERS
        // The reverse direction (instance -> static) always works fine
        // ============================================

        emp1.displayFullInfo();  // this instance method accesses BOTH emp1.name (instance)
        // AND Employee.companyName (static) internally


        // ============================================
        // SECTION 6: STATIC CONSTANTS (VERY COMMON PATTERN)
        // Combining 'static' with 'final' creates a true shared, unchangeable constant
        // ============================================

        System.out.println("Max employees allowed: " + Employee.MAX_EMPLOYEES);
        // Employee.MAX_EMPLOYEES = 500;  // COMPILE ERROR - final means it can't be reassigned


        // ============================================
        // SECTION 7: STATIC UTILITY METHODS (NO OBJECT NEEDED AT ALL)
        // A common pattern: methods that don't depend on any object's state,
        // just take input and produce output - perfect candidates for static
        // ============================================

        double bonus = Employee.calculateBonus(50000, 0.1);
        System.out.println("Calculated bonus: " + bonus);
        // Notice: called directly on the class, no Employee object was even created
        // for this calculation - it doesn't need one


        // ============================================
        // SECTION 8: STATIC BLOCKS
        // Code that runs ONCE, automatically, when the class is FIRST loaded
        // into memory - before main() even starts, before any object is created
        // Useful for one-time setup of static fields
        // ============================================

        System.out.println("Static block already ran before this line executed!");
        System.out.println("Initialized static list size: " + Employee.departments.size());


        // ============================================
        // SECTION 9: WHEN TO USE STATIC VS INSTANCE (DECISION GUIDE)
        // ============================================

        // Use INSTANCE when: the data/behavior is unique to each object
        //   (e.g., each employee's own name and salary)

        // Use STATIC when:
        //   - the data is shared/common across ALL objects (e.g., company name)
        //   - you're counting or tracking something across all objects
        //   - the method is a pure utility that doesn't need any object's state
        //   - it's a constant that never changes (combine with 'final')
    }
}


// ============================================
// THE CLASS DEFINITION
// ============================================

class Employee {

    // --- INSTANCE FIELDS: each object gets its own copy ---
    String name;
    double salary;

    // --- STATIC FIELDS: ONE shared copy across all objects ---
    static String companyName = "TechCorp";
    static int employeeCount = 0;  // tracks total objects created
    static final int MAX_EMPLOYEES = 1000;  // static + final = shared constant
    static java.util.ArrayList<String> departments = new java.util.ArrayList<>();

    // --- STATIC BLOCK ---
    // Runs exactly ONCE, when the class is first loaded - before any object
    // is created, and even before main() runs (if this class is used first)
    static {
        System.out.println("[Static block running - one-time setup]");
        departments.add("Engineering");
        departments.add("Sales");
        departments.add("HR");
    }

    // Constructor - runs EVERY TIME a new object is created
    Employee(String name, double salary) {
        this.name = name;       // instance field - unique per object
        this.salary = salary;   // instance field - unique per object
        employeeCount++;        // static field - shared counter increments for EVERY object
    }

    // --- INSTANCE METHOD ---
    // Can access BOTH instance fields (name, salary) AND static fields (companyName)
    void displayFullInfo() {
        System.out.println(name + " works at " + companyName + ", earning " + salary);
    }

    // --- STATIC METHOD ---
    // Can ONLY access other static members directly - no 'this', no instance fields
    static void printCompanyInfo() {
        System.out.println("Company: " + companyName + ", Total employees: " + employeeCount);
        // System.out.println(name);  // would NOT compile - no object context here
    }

    // --- STATIC UTILITY METHOD ---
    // Doesn't touch ANY field, static or instance - pure calculation based only
    // on its parameters. Classic candidate for static.
    static double calculateBonus(double baseSalary, double percentage) {
        return baseSalary * percentage;
    }
}