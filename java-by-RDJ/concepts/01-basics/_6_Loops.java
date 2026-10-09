public class _6_Loops {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: FOR LOOP
        // Best used when you know exactly how many times to repeat
        // Syntax: for (initialization; condition; update)
        // ============================================

        for (int i = 1; i <= 5; i++) {
            System.out.println("For loop iteration: " + i);
        }

        // Breakdown:
        // - initialization (int i = 1): runs ONCE at the very start
        // - condition (i <= 5): checked BEFORE each iteration; loop stops when false
        // - update (i++): runs AFTER each iteration


        // ============================================
        // SECTION 2: WHILE LOOP
        // Best used when you don't know the exact number of iterations in advance,
        // and want to keep going as long as a condition holds
        // Condition is checked BEFORE each iteration (may run 0 times)
        // ============================================

        int count = 1;
        while (count <= 5) {
            System.out.println("While loop count: " + count);
            count++;  // must manually update, or you get an infinite loop!
        }


        // ============================================
        // SECTION 3: DO-WHILE LOOP
        // Similar to while, BUT the condition is checked AFTER each iteration
        // Guarantees the loop body runs at least ONCE, even if condition is false
        // ============================================

        int attempts = 10;
        do {
            System.out.println("Do-while runs at least once, attempts = " + attempts);
            attempts++;
        } while (attempts < 5);  // condition is false immediately, but body still ran once above


        // ============================================
        // SECTION 4: NESTED LOOPS
        // A loop inside another loop - common for grids, tables, multiplication charts
        // ============================================

        System.out.println("Multiplication table (nested loop):");
        for (int row = 1; row <= 3; row++) {
            for (int col = 1; col <= 3; col++) {
                System.out.println(row + " x " + col + " = " + (row * col));
            }
        }
        // Outer loop runs 3 times; for EACH outer iteration, inner loop runs 3 times fully
        // Total inner executions: 3 x 3 = 9


        // ============================================
        // SECTION 5: BREAK STATEMENT
        // Immediately exits the loop entirely, skipping all remaining iterations
        // ============================================

        System.out.println("Using break:");
        for (int i = 1; i <= 10; i++) {
            if (i == 6) {
                break;  // stops the loop completely once i reaches 6
            }
            System.out.println("break demo, i = " + i);
        }
        // Output: prints 1 through 5, then stops (never prints 6 through 10)


        // ============================================
        // SECTION 6: CONTINUE STATEMENT
        // Skips ONLY the current iteration, then moves to the next one
        // Loop keeps running, just skips this specific cycle's remaining code
        // ============================================

        System.out.println("Using continue:");
        for (int i = 1; i <= 10; i++) {
            if (i % 2 == 0) {
                continue;  // skip printing for even numbers
            }
            System.out.println("continue demo, odd number: " + i);
        }
        // Output: prints only odd numbers 1, 3, 5, 7, 9


        // ============================================
        // SECTION 7: ENHANCED FOR LOOP (FOR-EACH)
        // Simplified syntax specifically for iterating over arrays/collections
        // Cannot access the index directly, and cannot modify the original array element
        // ============================================

        int[] numbers = {10, 20, 30, 40, 50};

        for (int num : numbers) {
            System.out.println("For-each value: " + num);
        }

        String[] names = {"Alice", "Bob", "Charlie"};
        for (String name : names) {
            System.out.println("Name: " + name);
        }


        // ============================================
        // SECTION 8: INFINITE LOOPS (AND HOW TO AVOID ACCIDENTAL ONES)
        // ============================================

        // Intentional infinite loop pattern (must have a break inside):
        int safetyCounter = 0;
        while (true) {
            System.out.println("Infinite loop iteration: " + safetyCounter);
            safetyCounter++;
            if (safetyCounter >= 3) {
                break;  // without this, it would run forever and crash/hang your program
            }
        }

        // Common ACCIDENTAL infinite loop bug (commented out - do not run as-is):
        // int mistake = 1;
        // while (mistake <= 5) {
        //     System.out.println(mistake);
        //     // forgot mistake++ here! condition never becomes false -> infinite loop
        // }


        // ============================================
        // SECTION 9: LABELED LOOPS (BREAKING OUT OF NESTED LOOPS)
        // Normally 'break' only exits the innermost loop.
        // A label lets you break out of an OUTER loop directly.
        // ============================================

        System.out.println("Labeled break demo:");
        outerLoop:
        for (int i = 1; i <= 3; i++) {
            for (int j = 1; j <= 3; j++) {
                if (i == 2 && j == 2) {
                    break outerLoop;  // exits BOTH loops immediately
                }
                System.out.println("i=" + i + ", j=" + j);
            }
        }
        // Without the label, 'break' alone would only stop the inner loop,
        // and the outer loop would continue to i=3


        // ============================================
        // SECTION 10: CHOOSING THE RIGHT LOOP
        // ============================================

        // Use 'for' when: you know the exact number of iterations in advance
        // Use 'while' when: iterations depend on a condition, count unknown upfront
        // Use 'do-while' when: you need the body to run at least once no matter what
        // Use 'for-each' when: simply iterating over every element in an array/collection
    }
}