public class _4_TypeCasting {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS TYPE CASTING?
        // Converting a value from one data type to another.
        // Two categories: Implicit (automatic) and Explicit (manual)
        // ============================================


        // ============================================
        // SECTION 2: IMPLICIT CASTING (WIDENING CONVERSION)
        // Smaller type -> Larger type
        // Done automatically by Java, NO data loss, NO explicit syntax needed
        //
        // Widening order (small to large):
        // byte -> short -> int -> long -> float -> double
        // (char can also widen to int)
        // ============================================

        byte byteValue = 10;
        short shortValue = byteValue;      // byte -> short, automatic
        int intValue = shortValue;         // short -> int, automatic
        long longValue = intValue;         // int -> long, automatic
        float floatValue = longValue;      // long -> float, automatic
        double doubleValue = floatValue;   // float -> double, automatic

        System.out.println("byte: " + byteValue);
        System.out.println("widened to short: " + shortValue);
        System.out.println("widened to int: " + intValue);
        System.out.println("widened to long: " + longValue);
        System.out.println("widened to float: " + floatValue);
        System.out.println("widened to double: " + doubleValue);

        // char widening to int (char is stored as a Unicode number under the hood)
        char letterGrade = 'A';
        int charToInt = letterGrade;   // 'A' -> 65
        System.out.println("char 'A' widened to int: " + charToInt);


        // ============================================
        // SECTION 3: EXPLICIT CASTING (NARROWING CONVERSION)
        // Larger type -> Smaller type
        // Must be done manually using (type) syntax
        // RISK: can lose data or precision
        //
        // Narrowing order (large to small):
        // double -> float -> long -> int -> short -> byte
        // ============================================

        double bigDouble = 99.99;
        float narrowedFloat = (float) bigDouble;
        long narrowedLong = (long) narrowedFloat;   // decimal part is TRUNCATED (not rounded!)
        int narrowedInt = (int) narrowedLong;
        short narrowedShort = (short) narrowedInt;
        byte narrowedByte = (byte) narrowedShort;

        System.out.println("Original double: " + bigDouble);
        System.out.println("Narrowed to float: " + narrowedFloat);
        System.out.println("Narrowed to long: " + narrowedLong);   // 99, decimal dropped
        System.out.println("Narrowed to int: " + narrowedInt);
        System.out.println("Narrowed to short: " + narrowedShort);
        System.out.println("Narrowed to byte: " + narrowedByte);


        // ============================================
        // SECTION 4: DATA LOSS EXAMPLES (IMPORTANT GOTCHAS)
        // Narrowing can silently produce WRONG results if you're not careful
        // ============================================

        // Example 1: Decimal truncation (not rounding!)
        double price = 9.99;
        int truncatedPrice = (int) price;
        System.out.println("9.99 cast to int: " + truncatedPrice);  // prints 9, NOT 10

        // Example 2: Overflow when narrowing a large number into a small type
        int largeNumber = 130;
        byte overflowedByte = (byte) largeNumber;
        System.out.println("130 cast to byte: " + overflowedByte);
        // byte range is -128 to 127, so 130 "wraps around" and becomes -126
        // This is a classic bug source - always check ranges before narrowing!

        // Example 3: Negative number overflow
        int negativeNumber = -200;
        byte negativeOverflow = (byte) negativeNumber;
        System.out.println("-200 cast to byte: " + negativeOverflow);


        // ============================================
        // SECTION 5: CASTING BETWEEN int AND char
        // char and int are closely related since char stores a Unicode number
        // ============================================

        int numberCode = 97;
        char resultChar = (char) numberCode;
        System.out.println("int 97 cast to char: " + resultChar);  // 'a'

        char sourceChar = 'z';
        int resultInt = sourceChar;   // widening, no cast needed
        System.out.println("char 'z' cast to int: " + resultInt);  // 122


        // ============================================
        // SECTION 6: STRING CONVERSIONS (NOT TECHNICALLY "CASTING")
        // Strings can't be cast like primitives - you must use conversion methods
        // ============================================

        // --- Number to String ---
        int number = 42;
        String numberAsString = String.valueOf(number);   // preferred way
        String numberAsString2 = "" + number;              // works, but less clean
        System.out.println("int to String: " + numberAsString);

        // --- String to Number ---
        String numericText = "123";
        int parsedInt = Integer.parseInt(numericText);
        double parsedDouble = Double.parseDouble("45.67");

        System.out.println("String to int: " + parsedInt);
        System.out.println("String to double: " + parsedDouble);

        // Careful: this throws a runtime error (NumberFormatException) if the
        // String isn't a valid number, e.g. Integer.parseInt("abc") would crash


        // ============================================
        // SECTION 7: MIXED-TYPE ARITHMETIC (AUTOMATIC PROMOTION)
        // When operating on two different types, Java automatically promotes
        // the smaller type to match the larger one before doing the math
        // ============================================

        int intNum = 10;
        double doubleNum = 3.5;

        double mixedResult = intNum + doubleNum;  // int is promoted to double automatically
        System.out.println("int + double = " + mixedResult);  // 13.5

        // But watch out with division involving two ints:
        int a = 7;
        int b = 2;
        System.out.println("int / int = " + (a / b));            // 3 (integer division)
        System.out.println("(double) int / int = " + ((double) a / b));  // 3.5 (cast fixes it)


        // ============================================
        // SECTION 8: WHEN TO USE EXPLICIT CASTING (REAL USE CASES)
        // ============================================

        // Use case 1: Calculating an average that needs decimal precision
        int totalScore = 270;
        int totalStudents = 8;
        double average = (double) totalScore / totalStudents;
        System.out.println("Average score: " + average);

        // Use case 2: Working with array/list indices (must be int, not double)
        double calculatedIndex = 3.9;
        int actualIndex = (int) calculatedIndex;  // truncates to 3, safe for indexing
        System.out.println("Index used: " + actualIndex);
    }
}