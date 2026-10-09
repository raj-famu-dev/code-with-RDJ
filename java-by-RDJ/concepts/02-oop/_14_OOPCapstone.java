import java.util.ArrayList;
import java.util.Objects;

public class _14_OOPCapstone {
    public static void main(String[] args) {

        // ============================================
        // CAPSTONE OVERVIEW
        // This program models a company's employee system, using:
        // - ENCAPSULATION: private fields, validated setters
        // - INHERITANCE: StaffMember -> Manager / Developer
        // - POLYMORPHISM: StaffMember[] array, each calculates pay differently
        // - ABSTRACTION: abstract StaffMember class + Mentor interface
        // - COMPOSITION: StaffMember HAS-A Address
        // - ENUMS: Department as a fixed set of constants
        // - STATIC: company-wide employee counter
        // - equals()/hashCode()/toString(): proper object identity
        // ============================================


        // ============================================
        // SECTION 1: CREATING OBJECTS (constructors + composition)
        // ============================================

        Address addr1 = new Address("123 Main St", "Austin", "TX");
        Address addr2 = new Address("456 Oak Ave", "Seattle", "WA");

        Manager manager = new Manager("Alice Chen", 95000, addr1, Department.ENGINEERING, 8);
        Developer dev1 = new Developer("Bob Singh", 78000, addr2, Department.ENGINEERING, "Java");
        Developer dev2 = new Developer("Cara Lopez", 82000, addr1, Department.PRODUCT, "Python");

        System.out.println("Total employees created: " + StaffMember.getEmployeeCount());
        System.out.println();


        // ============================================
        // SECTION 2: ENCAPSULATION - controlled access, validated changes
        // ============================================

        System.out.println("Manager's name (getter): " + manager.getName());
        manager.setBaseSalary(100000);  // valid raise
        System.out.println("After valid raise: $" + manager.getBaseSalary());

        manager.setBaseSalary(-500);    // invalid, should be rejected
        System.out.println("After invalid raise attempt: $" + manager.getBaseSalary());
        System.out.println();


        // ============================================
        // SECTION 3: POLYMORPHISM - one array, many behaviors
        // ============================================

        StaffMember[] staff = { manager, dev1, dev2 };

        System.out.println("--- Payroll Run (polymorphism in action) ---");
        for (StaffMember e : staff) {
            System.out.printf("%s (%s): $%.2f%n", e.getName(), e.getDepartment(), e.calculatePay());
        }
        System.out.println();


        // ============================================
        // SECTION 4: ABSTRACTION - shared structure, forced implementation
        // ============================================

        // StaffMember employee = new StaffMember(...);  // COMPILE ERROR - abstract, can't instantiate
        // Every subclass MUST implement calculatePay() - enforced by the compiler


        // ============================================
        // SECTION 5: INTERFACES - a separate, unrelated capability
        // Both Manager and Developer are StaffMembers (is-a), but only SOME
        // employees are also Mentors (a capability, not an identity)
        // ============================================

        System.out.println("--- Mentorship Check ---");
        for (StaffMember e : staff) {
            if (e instanceof Mentor mentor) {
                mentor.mentor();
            } else {
                System.out.println(e.getName() + " is not currently mentoring anyone.");
            }
        }
        System.out.println();


        // ============================================
        // SECTION 6: INHERITANCE - shared behavior, extended behavior
        // ============================================

        manager.displayInfo();   // shared method from StaffMember
        manager.holdMeeting();   // Manager's own additional method
        System.out.println();

        dev1.displayInfo();
        dev1.writeCode();        // Developer's own additional method
        System.out.println();


        // ============================================
        // SECTION 7: COMPOSITION - StaffMember HAS-A Address, not IS-A Address
        // ============================================

        System.out.println(dev1.getName() + " lives at: " + dev1.getAddress());
        System.out.println();


        // ============================================
        // SECTION 8: ENUMS - safe, fixed department categories
        // ============================================

        System.out.println("Department options:");
        for (Department d : Department.values()) {
            System.out.println("- " + d);
        }
        System.out.println();


        // ============================================
        // SECTION 9: equals(), hashCode(), toString() - proper object identity
        // ============================================

        Developer dev1Duplicate = new Developer("Bob Singh", 78000, addr2, Department.ENGINEERING, "Java");

        System.out.println("toString(): " + dev1);
        System.out.println("dev1 == dev1Duplicate (reference): " + (dev1 == dev1Duplicate));
        System.out.println("dev1.equals(dev1Duplicate) (content): " + dev1.equals(dev1Duplicate));

        ArrayList<StaffMember> allEmployees = new ArrayList<>();
        allEmployees.add(dev1);
        System.out.println("List contains an equal developer: " + allEmployees.contains(dev1Duplicate));
        // TRUE - because equals()/hashCode() are properly overridden,
        // .contains() correctly recognizes the logical duplicate
        System.out.println();


        // ============================================
        // SECTION 10: STATIC - shared, class-wide state
        // ============================================

        System.out.println("Final total employee count: " + StaffMember.getEmployeeCount());
        // Includes dev1Duplicate too, since the constructor ran and incremented
        // the shared static counter, regardless of logical "equality"
    }
}


// ============================================
// ENUM: fixed set of departments
// ============================================

enum Department {
    ENGINEERING, PRODUCT, SALES, HR
}


// ============================================
// COMPOSITION: Address is a separate object, contained inside StaffMember
// ============================================

class Address {
    private final String street;
    private final String city;
    private final String state;

    Address(String street, String city, String state) {
        this.street = street;
        this.city = city;
        this.state = state;
    }

    @Override
    public String toString() {
        return street + ", " + city + ", " + state;
    }
}


// ============================================
// INTERFACE: a capability some employees have, unrelated to the class hierarchy
// ============================================

interface Mentor {
    void mentor();
}


// ============================================
// ABSTRACT PARENT CLASS: shared structure + forced implementation
// ============================================

abstract class StaffMember {

    // --- ENCAPSULATION: private fields, controlled access ---
    private String name;
    private double baseSalary;
    private final Address address;      // COMPOSITION: StaffMember HAS-A Address
    private final Department department; // ENUM: fixed category

    // --- STATIC: shared across ALL StaffMember objects ---
    private static int employeeCount = 0;

    StaffMember(String name, double baseSalary, Address address, Department department) {
        this.name = name;
        this.baseSalary = baseSalary;
        this.address = address;
        this.department = department;
        employeeCount++;
    }

    static int getEmployeeCount() {
        return employeeCount;
    }

    // --- GETTERS ---
    String getName() {
        return name;
    }

    double getBaseSalary() {
        return baseSalary;
    }

    Address getAddress() {
        return address;
    }

    Department getDepartment() {
        return department;
    }

    // --- SETTER WITH VALIDATION (encapsulation in action) ---
    void setBaseSalary(double newSalary) {
        if (newSalary >= 0) {
            this.baseSalary = newSalary;
        } else {
            System.out.println("Rejected: salary cannot be negative.");
        }
    }

    // --- ABSTRACTION: every subclass MUST define its own pay calculation ---
    abstract double calculatePay();

    // --- SHARED CONCRETE METHOD: available to every subclass automatically ---
    void displayInfo() {
        System.out.println(name + " | " + department + " | Base salary: $" + baseSalary);
    }

    // --- equals()/hashCode()/toString() ---
    @Override
    public String toString() {
        return "StaffMember{name='" + name + "', department=" + department + "}";
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        StaffMember other = (StaffMember) obj;
        return Objects.equals(name, other.name) && department == other.department;
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, department);
    }
}


// ============================================
// CHILD CLASS 1: Manager - overrides calculatePay(), implements Mentor
// ============================================

class Manager extends StaffMember implements Mentor {

    private int teamSize;

    Manager(String name, double baseSalary, Address address, Department department, int teamSize) {
        super(name, baseSalary, address, department);
        this.teamSize = teamSize;
    }

    // --- POLYMORPHISM: Manager's own pay formula ---
    @Override
    double calculatePay() {
        return getBaseSalary() + (teamSize * 500);  // bonus per team member managed
    }

    void holdMeeting() {
        System.out.println(getName() + " is holding a team meeting with " + teamSize + " people.");
    }

    // --- INTERFACE IMPLEMENTATION ---
    @Override
    public void mentor() {
        System.out.println(getName() + " is mentoring junior team members.");
    }
}


// ============================================
// CHILD CLASS 2: Developer - overrides calculatePay(), NOT a Mentor
// ============================================

class Developer extends StaffMember {

    private String primaryLanguage;

    Developer(String name, double baseSalary, Address address, Department department, String primaryLanguage) {
        super(name, baseSalary, address, department);
        this.primaryLanguage = primaryLanguage;
    }

    // --- POLYMORPHISM: Developer's own, different pay formula ---
    @Override
    double calculatePay() {
        return getBaseSalary() + 2000;  // flat annual tooling stipend
    }

    void writeCode() {
        System.out.println(getName() + " is writing code in " + primaryLanguage + ".");
    }
}