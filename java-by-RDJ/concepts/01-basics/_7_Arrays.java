public class _7_Arrays {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS AN ARRAY?
        // A fixed-size container that holds multiple values of the SAME type,
        // stored in contiguous memory, accessed by index (starting at 0)
        // ============================================


        // ============================================
        // SECTION 2: DECLARING AND INITIALIZING ARRAYS
        // ============================================

        // Method 1: Declare, then assign size, then fill values individually
        int[] scores = new int[5];   // creates an array of 5 ints, all default to 0
        scores[0] = 90;
        scores[1] = 85;
        scores[2] = 78;
        scores[3] = 92;
        scores[4] = 88;

        // Method 2: Declare and initialize with values directly (shorthand)
        int[] ages = {21, 25, 19, 34, 40};

        // Method 3: Explicit 'new' with values (same result as Method 2)
        String[] fruits = new String[]{"Apple", "Banana", "Cherry"};

        System.out.println("First score: " + scores[0]);
        System.out.println("First age: " + ages[0]);
        System.out.println("First fruit: " + fruits[0]);


        // ============================================
        // SECTION 3: ACCESSING AND MODIFYING ELEMENTS
        // Arrays are ZERO-INDEXED: first element is index 0, not 1
        // ============================================

        System.out.println("Original age at index 2: " + ages[2]);
        ages[2] = 20;  // modifying an existing element
        System.out.println("Updated age at index 2: " + ages[2]);

        // Getting the array's length (property, not a method - no parentheses!)
        System.out.println("Length of ages array: " + ages.length);


        // ============================================
        // SECTION 4: LOOPING THROUGH ARRAYS
        // ============================================

        // Using a regular for loop (gives you access to the index)
        System.out.println("Scores using indexed for loop:");
        for (int i = 0; i < scores.length; i++) {
            System.out.println("Index " + i + ": " + scores[i]);
        }

        // Using enhanced for-each loop (simpler, but no index access)
        System.out.println("Fruits using for-each loop:");
        for (String fruit : fruits) {
            System.out.println(fruit);
        }


        // ============================================
        // SECTION 5: COMMON ARRAY OPERATIONS
        // ============================================

        // Finding the sum and average
        int sum = 0;
        for (int score : scores) {
            sum += score;
        }
        double average = (double) sum / scores.length;
        System.out.println("Sum of scores: " + sum);
        System.out.println("Average score: " + average);

        // Finding the maximum value
        int max = scores[0];
        for (int score : scores) {
            if (score > max) {
                max = score;
            }
        }
        System.out.println("Highest score: " + max);

        // Finding the minimum value
        int min = scores[0];
        for (int score : scores) {
            if (score < min) {
                min = score;
            }
        }
        System.out.println("Lowest score: " + min);


        // ============================================
        // SECTION 6: THE ArrayIndexOutOfBoundsException GOTCHA
        // Accessing an index that doesn't exist crashes the program at RUNTIME
        // (not caught at compile time!)
        // ============================================

        // Valid indices for 'ages' (length 5) are 0, 1, 2, 3, 4
        // ages[5] would throw: ArrayIndexOutOfBoundsException
        // Uncomment below to see the crash:
        // System.out.println(ages[5]);

        System.out.println("Valid last index of ages: " + ages[ages.length - 1]);


        // ============================================
        // SECTION 7: ARRAYS OF OTHER TYPES
        // ============================================

        double[] prices = {19.99, 45.50, 12.25};
        boolean[] flags = {true, false, true};
        char[] letters = {'J', 'A', 'V', 'A'};

        System.out.println("First price: " + prices[0]);
        System.out.println("First flag: " + flags[0]);
        System.out.println("Letters as chars: " + letters[0] + letters[1] + letters[2] + letters[3]);


        // ============================================
        // SECTION 8: 2D ARRAYS (ARRAYS OF ARRAYS)
        // Think of this like a grid/table - rows and columns
        // ============================================

        // Declaring a 2D array with fixed dimensions (2 rows, 3 columns)
        int[][] grid = new int[2][3];
        grid[0][0] = 1;
        grid[0][1] = 2;
        grid[0][2] = 3;
        grid[1][0] = 4;
        grid[1][1] = 5;
        grid[1][2] = 6;

        // Declaring and initializing directly (shorthand)
        int[][] matrix = {
                {1, 2, 3},
                {4, 5, 6},
                {7, 8, 9}
        };

        System.out.println("Element at grid[1][2]: " + grid[1][2]);
        System.out.println("Element at matrix[2][1]: " + matrix[2][1]);


        // ============================================
        // SECTION 9: LOOPING THROUGH 2D ARRAYS
        // Requires NESTED loops - outer loop for rows, inner loop for columns
        // ============================================

        System.out.println("Printing the full matrix:");
        for (int row = 0; row < matrix.length; row++) {
            for (int col = 0; col < matrix[row].length; col++) {
                System.out.print(matrix[row][col] + " ");
            }
            System.out.println();  // move to next line after each row
        }

        // Using enhanced for-each for 2D arrays
        System.out.println("Printing matrix using for-each:");
        for (int[] rowArray : matrix) {
            for (int value : rowArray) {
                System.out.print(value + " ");
            }
            System.out.println();
        }


        // ============================================
        // SECTION 10: ARRAYS ARE FIXED SIZE
        // Once created, an array's length CANNOT change.
        // If you need a resizable collection, use ArrayList instead
        // (covered in 03-collections)
        // ============================================

        int[] fixedArray = new int[3];
        System.out.println("Fixed array length: " + fixedArray.length);
        // fixedArray[3] = 10; // would crash - no index 3 exists in a length-3 array
        // There's no way to "add" a 4th element - you'd need to create a NEW array


        // ============================================
        // SECTION 11: COPYING ARRAYS
        // Simply doing arr2 = arr1 does NOT copy - it just points to the SAME array!
        // ============================================

        int[] original = {1, 2, 3};
        int[] wrongCopy = original;  // this is a REFERENCE copy, not a real copy
        wrongCopy[0] = 999;
        System.out.println("Original after 'wrong copy' modification: " + original[0]);
        // prints 999! because wrongCopy and original point to the SAME array in memory

        // Correct way to actually copy an array's contents:
        int[] realCopy = new int[original.length];
        for (int i = 0; i < original.length; i++) {
            realCopy[i] = original[i];
        }
        realCopy[0] = 111;
        System.out.println("Original after 'real copy' modification: " + original[0]);
        // stays 999 (from before), unaffected by realCopy's change - proves it's independent
    }
}