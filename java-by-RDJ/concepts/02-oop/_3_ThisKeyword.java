public class _3_ThisKeyword {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS 'this'?
        // 'this' is a reference to the CURRENT OBJECT - the specific instance
        // whose method or constructor is currently executing.
        // It lets an object refer to itself from within its own code.
        // ============================================

        Student student1 = new Student("Alice", 20);
        Student student2 = new Student("Bob", 22);

        student1.displayInfo();
        student2.displayInfo();


        // ============================================
        // SECTION 2: RESOLVING FIELD VS PARAMETER NAME CONFLICTS
        // (Recap from Constructors, but this is 'this' concept #1)
        // ============================================

        // See Student's constructor below: this.name = name;
        // Without 'this', Java would treat 'name = name' as assigning
        // the parameter to itself - the actual field stays null/unset


        // ============================================
        // SECTION 3: USING 'this' TO CALL ANOTHER METHOD IN THE SAME CLASS
        // Technically optional here (Java assumes 'this' automatically),
        // but sometimes used for clarity, or REQUIRED when a local variable
        // shadows a method name situation, or for stylistic emphasis
        // ============================================

        student1.celebrateBirthday();


        // ============================================
        // SECTION 4: PASSING 'this' AS AN ARGUMENT TO ANOTHER METHOD
        // Sometimes an object needs to pass ITSELF into another method/class,
        // so that method can operate on or reference the calling object
        // ============================================

        Library library = new Library();
        library.registerStudent(student1);
        library.registerStudent(student2);
        library.showAllRegistered();


        // ============================================
        // SECTION 5: RETURNING 'this' FROM A METHOD (METHOD CHAINING)
        // A method can return 'this' (the current object itself), allowing
        // you to CHAIN multiple method calls together in one statement
        // ============================================

        Student student3 = new Student("Charlie", 19);
        student3.setName("Charlie Updated").setAge(25).displayInfo();
        // Each setter returns 'this', so you can keep calling more methods
        // right after, instead of writing three separate statements


        // ============================================
        // SECTION 6: 'this' TO DISTINGUISH INSTANCE FIELD FROM LOCAL VARIABLE
        // (Not just constructor parameters - ANY local variable with the
        // same name as a field creates the same shadowing situation)
        // ============================================

        student1.updateAgeWithLocalShadowing(30);


        // ============================================
        // SECTION 7: 'this()' - CONSTRUCTOR CHAINING (RECAP)
        // Already covered in _2_Constructors.java, but listed here since
        // it IS technically a form of 'this' usage too, for completeness
        // ============================================

        Student student4 = new Student("Dana");  // chains internally to set default age
        student4.displayInfo();


        // ============================================
        // SECTION 8: WHY 'this' DOESN'T EXIST IN STATIC METHODS
        // 'this' refers to a specific OBJECT instance. Static methods belong
        // to the CLASS itself, not to any particular object - so there's no
        // "current object" for 'this' to point to. This would be a compile error:
        // ============================================

        // static void someStaticMethod() {
        //     System.out.println(this.someField); // COMPILE ERROR - no 'this' in static context
        // }
        // (We'll explore static vs instance fully in the next topic: _5_StaticVsInstance.java)
    }
}


// ============================================
// THE CLASS DEFINITION
// ============================================

class Student {

    String name;
    int age;

    // Constructor using 'this' to resolve field/parameter name conflict
    Student(String name, int age) {
        this.name = name;   // this.name = the FIELD, name = the PARAMETER
        this.age = age;
    }

    // Overloaded constructor chaining to the one above using this(...)
    Student(String name) {
        this(name, 18);  // default age if not provided
    }

    void displayInfo() {
        System.out.println("Student: " + this.name + ", Age: " + this.age);
        // 'this.name' here is optional (just 'name' would work identically),
        // but some developers always write 'this.' for fields, for readability
    }

    // Method calling another method using 'this' explicitly (optional but valid)
    void celebrateBirthday() {
        this.age = this.age + 1;
        System.out.println(this.name + " is now " + this.age + " (Happy Birthday!)");
        this.displayInfo();  // 'this.' is optional here too
    }

    // Methods that return 'this' to enable method chaining
    Student setName(String name) {
        this.name = name;
        return this;  // returns the current object itself
    }

    Student setAge(int age) {
        this.age = age;
        return this;
    }

    // Demonstrates 'this' resolving a LOCAL VARIABLE shadow (not just a parameter)
    void updateAgeWithLocalShadowing(int newAge) {
        int age = newAge;  // a local variable, NOT the field - just for demonstration
        this.age = age;    // 'this.age' = field, plain 'age' = the local variable above
        System.out.println("Updated via local shadowing demo, new age: " + this.age);
    }
}


// ============================================
// A SECOND CLASS DEMONSTRATING 'this' PASSED AS AN ARGUMENT
// ============================================

class Library {

    java.util.ArrayList<Student> registeredStudents = new java.util.ArrayList<>();

    void registerStudent(Student student) {
        registeredStudents.add(student);
        System.out.println(student.name + " has been registered to the library.");
    }

    void showAllRegistered() {
        System.out.println("All registered students:");
        for (Student s : registeredStudents) {
            System.out.println("- " + s.name);
        }
    }
}