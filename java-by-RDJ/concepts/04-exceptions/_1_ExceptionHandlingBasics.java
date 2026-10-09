public class _1_ExceptionHandlingBasics {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS AN EXCEPTION?
        // An exception is an unexpected event that disrupts normal program flow.
        // Without handling, it crashes the program immediately.
        // Java lets you "catch" these problems and respond gracefully instead.
        // ============================================


        // ============================================
        // SECTION 2: A CRASH WITHOUT HANDLING (WHAT WE'RE TRYING TO PREVENT)
        // Uncomment to see it crash the whole program:
        // ============================================

        // int result = 10 / 0;  // ArithmeticException: / by zero
        // System.out.println(result);  // this line never runs if the above crashes


        // ============================================
        // SECTION 3: BASIC try-catch
        // Code that MIGHT fail goes in 'try'.
        // If it fails, control jumps immediately to 'catch' instead of crashing.
        // ============================================

        try {
            int result = 10 / 0;
            System.out.println("This line never prints: " + result);
        } catch (ArithmeticException e) {
            System.out.println("Caught an error: " + e.getMessage());
        }

        System.out.println("Program continues running normally after the catch!");


        // ============================================
        // SECTION 4: try-catch-finally
        // 'finally' ALWAYS runs, whether an exception happened or not -
        // commonly used for cleanup (closing files, database connections, etc.)
        // ============================================

        try {
            int[] numbers = {1, 2, 3};
            System.out.println(numbers[5]);  // ArrayIndexOutOfBoundsException
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("Caught: " + e.getMessage());
        } finally {
            System.out.println("Finally block: this always runs, error or not.");
        }


        // ============================================
        // SECTION 5: MULTIPLE CATCH BLOCKS
        // Different exception types can be handled differently
        // Java checks each catch block top to bottom, uses the first match
        // ============================================

        try {
            String text = null;
            System.out.println(text.length());  // NullPointerException
        } catch (ArithmeticException e) {
            System.out.println("Arithmetic problem: " + e.getMessage());
        } catch (NullPointerException e) {
            System.out.println("Null pointer problem: " + e.getMessage());
        } catch (Exception e) {
            // generic fallback - catches anything not already matched above
            System.out.println("Some other problem: " + e.getMessage());
        }
        // IMPORTANT: order matters! More specific exceptions must come BEFORE
        // general ones (like Exception), or the general one "swallows" everything
        // and the specific catches become unreachable (compile error in Java, actually)


        // ============================================
        // SECTION 6: MULTI-CATCH (ONE BLOCK, MULTIPLE TYPES)
        // Use | when you want to handle several exception types the SAME way
        // ============================================

        try {
            int choice = 2;
            if (choice == 1) {
                int x = 5 / 0;
            } else {
                int[] arr = new int[2];
                int y = arr[10];
            }
        } catch (ArithmeticException | ArrayIndexOutOfBoundsException e) {
            System.out.println("Caught one of two possible errors: " + e.getMessage());
        }


        // ============================================
        // SECTION 7: CHECKED VS UNCHECKED EXCEPTIONS (CONCEPT PREVIEW)
        // Unchecked (RuntimeException and subclasses): NOT required to be
        //   caught or declared - compiler doesn't force you (e.g. ArithmeticException,
        //   NullPointerException, ArrayIndexOutOfBoundsException - all seen above)
        // Checked: MUST be either caught or declared with 'throws' -
        //   compiler enforces this (e.g. IOException, seen in file handling)
        // We'll cover this distinction in much more depth in 04-exceptions
        // ============================================


        // ============================================
        // SECTION 8: throw vs throws (QUICK PREVIEW)
        // 'throw' actually triggers an exception yourself
        // 'throws' declares that a method MIGHT produce a checked exception
        // (full custom exception coverage comes later in 04-exceptions)
        // ============================================

        try {
            checkAge(15);
        } catch (IllegalArgumentException e) {
            System.out.println("Validation failed: " + e.getMessage());
        }

        try {
            checkAge(25);
        } catch (IllegalArgumentException e) {
            System.out.println("Validation failed: " + e.getMessage());
        }


        // ============================================
        // SECTION 9: getMessage() vs printStackTrace()
        // getMessage() = short human-readable description
        // printStackTrace() = full technical detail, showing exactly where
        //   in the code the exception occurred (very useful for debugging)
        // ============================================

        try {
            int[] arr = new int[3];
            arr[10] = 1;
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("Message only: " + e.getMessage());
            System.out.println("Full stack trace below:");
            e.printStackTrace();
        }


        // ============================================
        // SECTION 10: WHY THIS MATTERS (REAL-WORLD CONNECTION)
        // Remember the Scanner nextBoolean() crash from _10_UserInput?
        // That crashed because we didn't wrap it in a try-catch.
        // Here's how that SAME situation would be handled properly:
        // ============================================

        java.util.Scanner scanner = new java.util.Scanner(System.in);
        System.out.print("Are you a student? (true/false): ");

        try {
            boolean isStudent = scanner.nextBoolean();
            System.out.println("Student status: " + isStudent);
        } catch (java.util.InputMismatchException e) {
            System.out.println("Invalid input - please type exactly 'true' or 'false'.");
        }

        scanner.close();
    }

    // Helper method demonstrating 'throw' - manually triggering an exception
    static void checkAge(int age) {
        if (age < 18) {
            throw new IllegalArgumentException("Age must be 18 or older, got: " + age);
        }
        System.out.println("Age " + age + " is valid.");
    }
}