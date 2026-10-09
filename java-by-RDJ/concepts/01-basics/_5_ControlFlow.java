public class _5_ControlFlow {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: IF STATEMENT
        // Executes a block of code only if a condition is true
        // ============================================

        int temperature = 35;

        if (temperature > 30) {
            System.out.println("It's hot outside.");
        }


        // ============================================
        // SECTION 2: IF-ELSE STATEMENT
        // Provides an alternative path when the condition is false
        // ============================================

        int age = 16;

        if (age >= 18) {
            System.out.println("You can vote.");
        } else {
            System.out.println("You cannot vote yet.");
        }


        // ============================================
        // SECTION 3: IF-ELSE IF-ELSE CHAIN
        // Used when there are multiple conditions to check in sequence
        // Java checks each condition top to bottom, stops at the first true one
        // ============================================

        int score = 72;

        if (score >= 90) {
            System.out.println("Grade: A");
        } else if (score >= 80) {
            System.out.println("Grade: B");
        } else if (score >= 70) {
            System.out.println("Grade: C");
        } else if (score >= 60) {
            System.out.println("Grade: D");
        } else {
            System.out.println("Grade: F");
        }
        // Note: only ONE branch runs, even if multiple conditions would be true.
        // score=72 satisfies both >=70 and >=60, but only the first match ("C") runs.


        // ============================================
        // SECTION 4: NESTED IF STATEMENTS
        // An if statement inside another if statement
        // ============================================

        boolean hasTicket = true;
        int visitorAge = 25;

        if (hasTicket) {
            if (visitorAge >= 18) {
                System.out.println("Entry allowed: Adult with ticket.");
            } else {
                System.out.println("Entry denied: Minor, even with ticket.");
            }
        } else {
            System.out.println("Entry denied: No ticket.");
        }


        // ============================================
        // SECTION 5: LOGICAL OPERATORS IN CONDITIONS
        // Combine multiple conditions instead of nesting (often cleaner)
        // ============================================

        boolean isWeekend = true;
        boolean isHoliday = false;

        if (isWeekend || isHoliday) {
            System.out.println("No work today!");
        } else {
            System.out.println("It's a work day.");
        }

        int accountBalance = 500;
        boolean isVerified = true;

        if (accountBalance > 0 && isVerified) {
            System.out.println("Transaction approved.");
        } else {
            System.out.println("Transaction denied.");
        }


        // ============================================
        // SECTION 6: SWITCH STATEMENT (TRADITIONAL STYLE)
        // Cleaner alternative to long if-else chains when checking
        // ONE variable against many fixed values
        // ============================================

        int dayNumber = 3;
        String dayName;

        switch (dayNumber) {
            case 1:
                dayName = "Monday";
                break;
            case 2:
                dayName = "Tuesday";
                break;
            case 3:
                dayName = "Wednesday";
                break;
            case 4:
                dayName = "Thursday";
                break;
            case 5:
                dayName = "Friday";
                break;
            case 6:
                dayName = "Saturday";
                break;
            case 7:
                dayName = "Sunday";
                break;
            default:
                dayName = "Invalid day number";
                break;
        }

        System.out.println("Day: " + dayName);

        // IMPORTANT: forgetting 'break' causes "fall-through" -
        // execution continues into the NEXT case even if it doesn't match.
        // This is a very common beginner bug. Example below (commented out):
        //
        // switch (2) {
        //     case 1: System.out.println("One");
        //     case 2: System.out.println("Two");   // this runs
        //     case 3: System.out.println("Three");  // this ALSO runs (no break above it)
        //     default: System.out.println("Default");
        // }
        // Output would be: Two, Three, Default (all printed)


        // ============================================
        // SECTION 7: SWITCH EXPRESSION (MODERN STYLE, Java 14+)
        // Cleaner syntax using arrows, no fall-through risk, can return a value directly
        // ============================================

        int monthNumber = 4;

        String season = switch (monthNumber) {
            case 12, 1, 2 -> "Winter";
            case 3, 4, 5 -> "Spring";
            case 6, 7, 8 -> "Summer";
            case 9, 10, 11 -> "Autumn";
            default -> "Invalid month";
        };

        System.out.println("Season: " + season);

        // Notice: no 'break' needed, multiple values per case with commas,
        // and it directly assigns the result to a variable


        // ============================================
        // SECTION 8: TERNARY AS A CONTROL FLOW SHORTCUT
        // (Recap from Operators - useful for simple two-way branches)
        // ============================================

        int number = 15;
        String parity = (number % 2 == 0) ? "Even" : "Odd";
        System.out.println(number + " is " + parity);


        // ============================================
        // SECTION 9: COMMON PITFALLS TO AVOID
        // ============================================

        // Pitfall 1: Using = instead of == (assignment vs comparison)
        int pitfallValue = 10;
        if (pitfallValue == 10) {   // correct: comparing
            System.out.println("Correct comparison works.");
        }
        // if (pitfallValue = 10) would actually be a COMPILE ERROR in Java
        // (unlike some other languages) since it doesn't evaluate to boolean - Java protects you here

        // Pitfall 2: Dangling else - always use braces {} even for single-line ifs
        // to avoid ambiguity and bugs when you add more lines later
        int x = 5;
        if (x > 0) {
            System.out.println("x is positive");
        } else {
            System.out.println("x is zero or negative");
        }
    }
}