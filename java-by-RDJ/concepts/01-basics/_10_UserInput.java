import java.util.Scanner;

public class _10_UserInput {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS Scanner?
        // Scanner is a built-in Java class used to read input from the user
        // (via the console/terminal). It needs to be imported at the top of the file.
        // ============================================

        Scanner scanner = new Scanner(System.in);
        // System.in represents the "standard input" - normally your keyboard


        // ============================================
        // SECTION 2: READING A STRING (FULL LINE)
        // nextLine() reads everything typed until Enter is pressed, INCLUDING spaces
        // ============================================

        System.out.print("Enter your name: ");
        String userName = scanner.nextLine();
        System.out.println("Hello, " + userName + "!");


        // ============================================
        // SECTION 3: READING A SINGLE WORD (NO SPACES)
        // next() reads only up to the next space/whitespace, not a full line
        // ============================================

        System.out.print("Enter your favorite programming language (one word): ");
        String language = scanner.next();
        System.out.println("You chose: " + language);


        // ============================================
        // SECTION 4: READING NUMBERS
        // Scanner has specific methods for each numeric type
        // ============================================

        System.out.print("Enter your age (int): ");
        int age = scanner.nextInt();
        System.out.println("You are " + age + " years old.");

        System.out.print("Enter your height in meters (double): ");
        double height = scanner.nextDouble();
        System.out.println("Your height is " + height + "m.");


        // ============================================
        // SECTION 5: READING A BOOLEAN
        // Must type exactly "true" or "false" (case-insensitive)
        // ============================================

        System.out.print("Are you a student? (true/false): ");
        boolean isStudent = scanner.nextBoolean();
        System.out.println("Student status: " + isStudent);


        // ============================================
        // SECTION 6: THE CLASSIC nextInt() + nextLine() BUG
        // This trips up almost every beginner at least once!
        // ============================================

        // Problem: nextInt() reads the NUMBER but leaves the leftover "newline"
        // character in the input buffer. The very next nextLine() call then
        // reads that leftover empty leftover instead of waiting for new input.

        System.out.print("Enter a number: ");
        int number = scanner.nextInt();

        scanner.nextLine();  // <-- THE FIX: consume the leftover newline character
        // Without this line above, the next nextLine() call below would be
        // skipped silently, grabbing "" instead of what you intended to type

        System.out.print("Now enter a sentence: ");
        String sentence = scanner.nextLine();

        System.out.println("Number: " + number);
        System.out.println("Sentence: " + sentence);


        // ============================================
        // SECTION 7: READING MULTIPLE VALUES ON ONE LINE
        // You can chain reads if the user separates values with spaces
        // ============================================

        System.out.print("Enter three numbers separated by spaces: ");
        int num1 = scanner.nextInt();
        int num2 = scanner.nextInt();
        int num3 = scanner.nextInt();
        System.out.println("Sum: " + (num1 + num2 + num3));


        // ============================================
        // SECTION 8: VALIDATING INPUT WITH hasNextInt() ETC.
        // Prevents crashes when the user types something unexpected
        // ============================================

        scanner.nextLine();  // clear leftover newline again before this section

        System.out.print("Enter your favorite number: ");
        if (scanner.hasNextInt()) {
            int favoriteNumber = scanner.nextInt();
            System.out.println("Great choice: " + favoriteNumber);
        } else {
            System.out.println("That wasn't a valid number!");
            scanner.next();  // consume the invalid input so it doesn't cause issues later
        }


        // ============================================
        // SECTION 9: CLOSING THE SCANNER
        // Good practice to close it when you're done reading input,
        // to free up system resources (especially important in larger programs)
        // ============================================

        scanner.close();

        // WARNING: once closed, you cannot read from this Scanner again -
        // trying to call scanner.nextLine() etc. after close() throws an exception.
        // Only close it when you're TRULY done with all input for the program.
    }
}