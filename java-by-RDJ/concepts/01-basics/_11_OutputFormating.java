public class _11_OutputFormating {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THE THREE BASIC PRINT METHODS
        // ============================================

        System.out.println("This prints text AND moves to a new line after");
        System.out.print("This prints text but stays on the SAME line... ");
        System.out.print("...so this continues right after it");
        System.out.println();  // empty println just moves to the next line

        System.err.println("This prints to the ERROR stream (shows in red in most IDEs)");
        // System.err is used for error messages - IntelliJ displays it in red text,
        // separate from normal output, useful for distinguishing errors from regular output


        // ============================================
        // SECTION 2: PRINTF - FORMATTED OUTPUT
        // printf() lets you control EXACTLY how values are displayed
        // using format specifiers like %d, %s, %f, etc.
        // ============================================

        String name = "RDJ";
        int age = 25;
        double salary = 55000.5;

        System.out.printf("Name: %s, Age: %d, Salary: %f%n", name, age, salary);
        // %s = String, %d = integer (decimal), %f = floating point, %n = newline (safer than \n)


        // ============================================
        // SECTION 3: COMMON FORMAT SPECIFIERS
        // ============================================

        System.out.printf("String: %s%n", "Hello");
        System.out.printf("Integer: %d%n", 42);
        System.out.printf("Float/Double: %f%n", 3.14159);
        System.out.printf("Character: %c%n", 'A');
        System.out.printf("Boolean: %b%n", true);
        System.out.printf("Percent literal: 100%%%n");  // %% prints an actual % symbol


        // ============================================
        // SECTION 4: CONTROLLING DECIMAL PRECISION
        // %.Nf shows exactly N digits after the decimal point
        // ============================================

        double pi = 3.14159265;

        System.out.printf("Default: %f%n", pi);           // 3.141593 (6 decimals by default)
        System.out.printf("2 decimals: %.2f%n", pi);       // 3.14
        System.out.printf("4 decimals: %.4f%n", pi);       // 3.1416 (rounds, doesn't truncate!)
        System.out.printf("0 decimals: %.0f%n", pi);        // 3


        // ============================================
        // SECTION 5: CONTROLLING FIELD WIDTH (ALIGNMENT)
        // A number before the specifier sets minimum width;
        // useful for lining up columns of data
        // ============================================

        System.out.printf("[%10d]%n", 42);      // right-aligned, padded to 10 characters wide
        System.out.printf("[%-10d]%n", 42);     // left-aligned (minus sign flips alignment), padded
        System.out.printf("[%10s]%n", "Hi");    // works for strings too
        System.out.printf("[%-10s]%n", "Hi");


        // ============================================
        // SECTION 6: PRACTICAL EXAMPLE - ALIGNED TABLE OUTPUT
        // Combining width + decimal control to make a clean-looking table
        // ============================================

        String[] items = {"Apple", "Bread", "Milk"};
        double[] prices = {1.50, 3.25, 2.10};

        System.out.printf("%-10s %10s%n", "Item", "Price");
        System.out.printf("%-10s %10s%n", "----", "-----");
        for (int i = 0; i < items.length; i++) {
            System.out.printf("%-10s %10.2f%n", items[i], prices[i]);
        }


        // ============================================
        // SECTION 7: String.format() - SAME RULES, BUT RETURNS A STRING
        // Useful when you want to STORE the formatted text instead of
        // immediately printing it (e.g., to use it later, or build a message)
        // ============================================

        String formattedMessage = String.format("Hello %s, you are %d years old.", name, age);
        System.out.println(formattedMessage);

        // Great for building reusable formatted strings
        String receiptLine = String.format("%-15s $%8.2f", "Coffee", 4.5);
        System.out.println(receiptLine);


        // ============================================
        // SECTION 8: ESCAPE SEQUENCES IN STRINGS
        // Special characters that need a backslash to be interpreted correctly
        // ============================================

        System.out.println("Newline example:\nThis is on a new line");
        System.out.println("Tab example:\tThis is tabbed over");
        System.out.println("Quote example: \"This is in quotes\"");
        System.out.println("Backslash example: C:\\Users\\RDJ");
        System.out.println("Carriage return \\n vs %n note: \\n works but %n is safer");
        // \n always means "line feed" specifically, but %n adapts to the operating
        // system's actual newline convention (matters more in file writing than console)


        // ============================================
        // SECTION 9: TEXT BLOCKS (Java 15+) - MULTI-LINE STRINGS MADE EASY
        // Triple-quote syntax lets you write multi-line text without \n everywhere
        // ============================================

        String textBlock = """
                This is a text block.
                It spans multiple lines
                without needing \\n characters.
                Great for JSON, HTML, or SQL snippets.
                """;

        System.out.println(textBlock);


        // ============================================
        // SECTION 10: NUMBER FORMATTING WITH COMMAS (LOCALE-AWARE)
        // Useful for displaying large numbers in a readable way
        // ============================================

        int largeNumber = 1234567;
        System.out.printf("With commas: %,d%n", largeNumber);   // 1,234,567

        double largeMoney = 9876543.21;
        System.out.printf("Money with commas: $%,.2f%n", largeMoney);  // $9,876,543.21
    }
}