public class _9_Methods {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS A METHOD?
        // A reusable block of code that performs a specific task.
        // Helps avoid repeating the same code, and makes programs organized/readable.
        // ============================================

        // Calling a simple method (defined below in this same class)
        greetUser();


        // ============================================
        // SECTION 2: METHODS WITH PARAMETERS
        // Parameters let you pass data INTO a method
        // ============================================

        greetByName("RDJ");
        greetByName("Anthropic");


        // ============================================
        // SECTION 3: METHODS WITH RETURN VALUES
        // 'return' sends a value BACK to whoever called the method
        // The return type in the method signature must match what's returned
        // ============================================

        int sum = addNumbers(5, 10);
        System.out.println("Sum from method: " + sum);

        double average = calculateAverage(85, 92, 78);
        System.out.println("Average from method: " + average);


        // ============================================
        // SECTION 4: METHODS WITH MULTIPLE PARAMETERS
        // ============================================

        printProfile("RDJ", 25, true);


        // ============================================
        // SECTION 5: METHOD OVERLOADING
        // Multiple methods with the SAME name but DIFFERENT parameter lists
        // (different number of params, or different types)
        // Java decides which one to call based on the arguments you pass
        // ============================================

        System.out.println("Overload with 2 ints: " + add(3, 4));
        System.out.println("Overload with 3 ints: " + add(3, 4, 5));
        System.out.println("Overload with 2 doubles: " + add(3.5, 4.5));
        System.out.println("Overload with String: " + add("Hello", "World"));


        // ============================================
        // SECTION 6: void VS RETURN TYPE METHODS
        // 'void' means the method does something but gives nothing back
        // Any other type means it MUST return a value of that type
        // ============================================

        printMessage("This method returns nothing");  // void - just performs an action
        String result = buildMessage("This method returns a value");
        System.out.println(result);


        // ============================================
        // SECTION 7: PASS BY VALUE (IMPORTANT CONCEPT)
        // Java passes a COPY of the value into a method.
        // Changing a parameter INSIDE the method does NOT affect the original variable.
        // ============================================

        int originalNumber = 10;
        System.out.println("Before method call: " + originalNumber);
        modifyValue(originalNumber);
        System.out.println("After method call: " + originalNumber);
        // Still 10! The method modified its own local COPY, not the original variable


        // ============================================
        // SECTION 8: PASS BY VALUE WITH ARRAYS (THE TRICKY EXCEPTION)
        // Arrays are objects - the "copy" passed is a copy of the REFERENCE,
        // which still points to the SAME array in memory.
        // So changes to array CONTENTS inside a method DO persist outside.
        // ============================================

        int[] numbers = {1, 2, 3};
        System.out.println("Before array method call: " + numbers[0]);
        modifyArray(numbers);
        System.out.println("After array method call: " + numbers[0]);
        // This DOES change! Because 'numbers' and the parameter both point to
        // the same array object in memory


        // ============================================
        // SECTION 9: VARARGS (VARIABLE NUMBER OF ARGUMENTS)
        // Lets a method accept ANY number of arguments of the same type
        // ============================================

        System.out.println("Varargs sum (2 args): " + sumAll(1, 2));
        System.out.println("Varargs sum (5 args): " + sumAll(1, 2, 3, 4, 5));
        System.out.println("Varargs sum (0 args): " + sumAll());


        // ============================================
        // SECTION 10: RECURSION (A METHOD CALLING ITSELF)
        // Must have a "base case" to stop, or it runs forever (StackOverflowError)
        // ============================================

        System.out.println("Factorial of 5: " + factorial(5));
    }


    // ============================================
    // METHOD DEFINITIONS BELOW
    // 'static' is used here because main() is static, and static methods
    // can only directly call other static methods without creating an object
    // (object-based calling is covered in 02-oop)
    // ============================================

    // Simple method - no parameters, no return value
    static void greetUser() {
        System.out.println("Welcome to Java Methods!");
    }

    // Method with one parameter
    static void greetByName(String userName) {
        System.out.println("Hello, " + userName + "!");
    }

    // Method with parameters AND a return value
    static int addNumbers(int a, int b) {
        return a + b;
    }

    static double calculateAverage(int a, int b, int c) {
        return (a + b + c) / 3.0;  // .0 ensures decimal division, not integer division
    }

    // Method with multiple different-typed parameters
    static void printProfile(String name, int age, boolean isActive) {
        System.out.println("Name: " + name + ", Age: " + age + ", Active: " + isActive);
    }

    // --- Overloaded methods (same name, different parameter signatures) ---
    static int add(int a, int b) {
        return a + b;
    }

    static int add(int a, int b, int c) {
        return a + b + c;
    }

    static double add(double a, double b) {
        return a + b;
    }

    static String add(String a, String b) {
        return a + " " + b;  // "adds" strings by concatenating
    }

    // void method example
    static void printMessage(String msg) {
        System.out.println(msg);
    }

    // Return-type method example
    static String buildMessage(String msg) {
        return "Built message: " + msg;
    }

    // Demonstrates pass-by-value with primitives (no lasting effect outside)
    static void modifyValue(int value) {
        value = value + 100;  // only changes the LOCAL copy
        System.out.println("Inside method, value is now: " + value);
    }

    // Demonstrates pass-by-value with arrays (DOES affect the original, since
    // both point to the same array object)
    static void modifyArray(int[] arr) {
        arr[0] = 999;  // modifies the actual array content
    }

    // Varargs method - the '...' syntax means "zero or more int arguments"
    static int sumAll(int... nums) {
        int total = 0;
        for (int n : nums) {
            total += n;
        }
        return total;
    }

    // Recursive method - calls itself with a smaller input each time
    static int factorial(int n) {
        if (n <= 1) {
            return 1;  // base case - stops the recursion
        }
        return n * factorial(n - 1);  // recursive case - calls itself
    }
}