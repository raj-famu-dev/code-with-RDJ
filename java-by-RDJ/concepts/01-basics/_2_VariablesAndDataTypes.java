public class _2_VariablesAndDataTypes{

    static void main() {
        // ============================================
        // SECTION 1: PRIMITIVE DATA TYPES
        // Java has 8 primitive types - these store actual values directly,
        // not references to objects.
        // ============================================

        // --- Integer types (whole numbers, no decimals) ---
        byte myByte = 100;              // 8-bit, range: -128 to 127
        short myShort = 30000;          // 16-bit, range: -32,768 to 32,767
        int myInt = 2_000_000;          // 32-bit, most commonly used integer type
        long myLong = 15000000000L;     // 64-bit, needs 'L' suffix for large values

        System.out.println("byte: " + myByte);
        System.out.println("short: " + myShort);
        System.out.println("int: " + myInt);
        System.out.println("long: " + myLong);

        // --- Floating-point types (decimal numbers) ---
        float myFloat = 5.75f;          // 32-bit, needs 'f' suffix
        double myDouble = 19.99;        // 64-bit, default choice for decimals (more precision)

        System.out.println("float: " + myFloat);
        System.out.println("double: " + myDouble);

        // --- Character type (single character) ---
        char myChar = 'A';              // single quotes, stores one character
        char myCharFromNumber = 66;     // chars are actually numbers under the hood (Unicode)
        // 66 corresponds to 'B'

        System.out.println("char: " + myChar);
        System.out.println("char from number: " + myCharFromNumber);

        // --- Boolean type (true/false only) ---
        boolean isJavaFun = true;
        boolean isLearningDone = false;

        System.out.println("boolean 1: " + isJavaFun);
        System.out.println("boolean 2: " + isLearningDone);


        // ============================================
        // SECTION 2: NON-PRIMITIVE (REFERENCE) TYPE - STRING
        // Strings are NOT primitives - they are objects.
        // They store references to String objects in memory.
        // ============================================

        String myName = "RDJ";
        String greeting = "Hello, " + myName + "!";  // string concatenation with +

        System.out.println(greeting);
        System.out.println("String length: " + greeting.length());
        System.out.println("Uppercase: " + greeting.toUpperCase());


        // ============================================
        // SECTION 3: TYPE CASTING
        // Converting one data type into another.
        // ============================================

        // --- Implicit casting (widening) ---
        // Smaller type -> Larger type. Happens automatically, no data loss.
        int intValue = 100;
        double widenedToDouble = intValue;  // int -> double, automatic
        System.out.println("Widening int to double: " + widenedToDouble);

        // --- Explicit casting (narrowing) ---
        // Larger type -> Smaller type. Must be done manually, can lose data.
        double doubleValue = 9.78;
        int narrowedToInt = (int) doubleValue;  // double -> int, decimal is TRUNCATED (not rounded)
        System.out.println("Narrowing double to int: " + narrowedToInt);  // prints 9, not 10

        // --- Casting between int and char ---
        int numberForChar = 65;
        char resultChar = (char) numberForChar;  // 65 -> 'A'
        System.out.println("int to char: " + resultChar);


        // ============================================
        // SECTION 4: CONSTANTS
        // Use 'final' when a value should NEVER change after assignment.
        // Convention: constants are named in ALL_CAPS with underscores.
        // ============================================

        final double PI = 3.14159;
        final int MAX_USERS = 100;

        System.out.println("Constant PI: " + PI);
        // PI = 3.14; // <-- this would cause a compile error if uncommented


        // ============================================
        // SECTION 5: VAR - TYPE INFERENCE (Java 10+)
        // 'var' lets the compiler figure out the type automatically.
        // It's still strongly typed - just less typing for you.
        // ============================================

        var inferredInt = 42;              // compiler infers: int
        var inferredString = "Auto-typed"; // compiler infers: String
        var inferredDouble = 3.14;         // compiler infers: double

        System.out.println("var int: " + inferredInt);
        System.out.println("var String: " + inferredString);
        System.out.println("var double: " + inferredDouble);


        // ============================================
        // SECTION 6: VARIABLE NAMING RULES & CONVENTIONS
        // ============================================

        // Rules (must follow):
        // - Can contain letters, digits, underscore, dollar sign
        // - Cannot start with a digit
        // - Cannot be a reserved keyword (like 'class', 'int', 'public')
        // - Case-sensitive (age and Age are different variables)

        // Conventions (best practice, not enforced by compiler):
        // - Use camelCase for variables and methods: firstName, totalAmount
        // - Use PascalCase for class names: VariablesAndDataTypes
        // - Use ALL_CAPS for constants: MAX_USERS, PI

        int studentAge = 21;  // good: camelCase, descriptive name
        System.out.println("Student age: " + studentAge);
    }
}

