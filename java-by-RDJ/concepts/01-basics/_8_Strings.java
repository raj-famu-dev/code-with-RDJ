public class _8_Strings {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS A STRING?
        // A String is NOT a primitive - it's an object (reference type)
        // that represents a sequence of characters.
        // Strings are IMMUTABLE - once created, their content can never change.
        // ============================================

        String greeting = "Hello";
        String name = "RDJ";


        // ============================================
        // SECTION 2: CREATING STRINGS
        // ============================================

        // Method 1: String literal (preferred - Java reuses identical literals via "String Pool")
        String str1 = "Java";

        // Method 2: Using 'new' keyword (creates a genuinely new object, bypasses String Pool)
        String str2 = new String("Java");

        System.out.println("str1: " + str1);
        System.out.println("str2: " + str2);

        // Gotcha: str1 == str2 is FALSE even though content is identical!
        // == compares references (memory addresses), not content, for objects
        System.out.println("str1 == str2 (reference check): " + (str1 == str2));
        System.out.println("str1.equals(str2) (content check): " + (str1.equals(str2)));
        // ALWAYS use .equals() to compare String content, never ==


        // ============================================
        // SECTION 3: STRING CONCATENATION
        // ============================================

        String fullGreeting = greeting + ", " + name + "!";
        System.out.println(fullGreeting);

        // Using += for concatenation
        String message = "Java";
        message += " is";
        message += " powerful";
        System.out.println(message);

        // Concatenating with numbers (auto-converts to String)
        int age = 25;
        String combined = "Age: " + age;
        System.out.println(combined);


        // ============================================
        // SECTION 4: STRING IMMUTABILITY (IMPORTANT CONCEPT)
        // Every "modification" actually creates a NEW String object -
        // it never changes the original.
        // ============================================

        String original = "Hello";
        String modified = original.concat(" World");

        System.out.println("Original (unchanged): " + original);
        System.out.println("Modified (new object): " + modified);
        // 'original' is still "Hello" - concat() returned a brand new String


        // ============================================
        // SECTION 5: COMMON STRING METHODS
        // ============================================

        String sample = "  Java Programming  ";

        // length() - number of characters
        System.out.println("Length: " + sample.length());

        // trim() - removes leading/trailing whitespace
        System.out.println("Trimmed: '" + sample.trim() + "'");

        // toUpperCase() / toLowerCase()
        System.out.println("Uppercase: " + sample.trim().toUpperCase());
        System.out.println("Lowercase: " + sample.trim().toLowerCase());

        // charAt(index) - get a single character at a position
        String word = "Java";
        System.out.println("Character at index 0: " + word.charAt(0));
        System.out.println("Character at index 3: " + word.charAt(3));

        // indexOf() - find position of a substring/character (-1 if not found)
        String sentence = "I love Java programming";
        System.out.println("Index of 'Java': " + sentence.indexOf("Java"));
        System.out.println("Index of 'Python': " + sentence.indexOf("Python"));  // -1, not found

        // substring(start) and substring(start, end) - extract a portion
        System.out.println("Substring from index 7: " + sentence.substring(7));
        System.out.println("Substring from 7 to 11: " + sentence.substring(7, 11));
        // end index is EXCLUSIVE - so (7, 11) gives characters at 7,8,9,10 only

        // replace() - replace all occurrences of a substring
        String replaced = sentence.replace("Java", "Python");
        System.out.println("Replaced: " + replaced);

        // contains() - check if a substring exists
        System.out.println("Contains 'love': " + sentence.contains("love"));

        // equals() vs equalsIgnoreCase()
        System.out.println("'JAVA'.equals('java'): " + "JAVA".equals("java"));
        System.out.println("'JAVA'.equalsIgnoreCase('java'): " + "JAVA".equalsIgnoreCase("java"));

        // startsWith() / endsWith()
        System.out.println("Starts with 'I': " + sentence.startsWith("I"));
        System.out.println("Ends with 'programming': " + sentence.endsWith("programming"));

        // isEmpty() / isBlank()
        String emptyStr = "";
        String blankStr = "   ";
        System.out.println("isEmpty on '': " + emptyStr.isEmpty());
        System.out.println("isBlank on '   ': " + blankStr.isBlank());   // true - whitespace only
        System.out.println("isEmpty on '   ': " + blankStr.isEmpty());   // false - has characters (spaces)


        // ============================================
        // SECTION 6: SPLITTING AND JOINING STRINGS
        // ============================================

        // split() - breaks a String into an array based on a delimiter
        String csvData = "Alice,Bob,Charlie,Dave";
        String[] namesArray = csvData.split(",");

        System.out.println("Split result:");
        for (String n : namesArray) {
            System.out.println("- " + n);
        }

        // String.join() - opposite of split, combines array elements with a delimiter
        String[] words = {"Java", "is", "fun"};
        String joined = String.join(" ", words);
        System.out.println("Joined: " + joined);


        // ============================================
        // SECTION 7: STRINGBUILDER (FOR EFFICIENT STRING MODIFICATION)
        // Since Strings are immutable, repeated concatenation in a loop
        // is inefficient (creates many throwaway objects).
        // StringBuilder is MUTABLE - use it for heavy string building.
        // ============================================

        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= 5; i++) {
            sb.append("Number").append(i).append(" ");
        }
        System.out.println("StringBuilder result: " + sb.toString());

        // StringBuilder also supports insert, delete, reverse
        StringBuilder sb2 = new StringBuilder("Hello");
        sb2.append(" World");           // "Hello World"
        sb2.insert(5, ",");              // "Hello, World"
        sb2.reverse();                   // reverses the entire thing
        System.out.println("StringBuilder manipulated: " + sb2.toString());


        // ============================================
        // SECTION 8: COMPARING STRINGS PROPERLY
        // ============================================

        String password1 = "secret123";
        String password2 = "secret123";
        String password3 = new String("secret123");

        // Literals from the String Pool - Java reuses them, so == happens to work here
        System.out.println("password1 == password2: " + (password1 == password2));  // true (pool reuse)

        // But with 'new', it's a separate object - == fails even with identical content
        System.out.println("password1 == password3: " + (password1 == password3));  // false

        // The SAFE way, always:
        System.out.println("password1.equals(password3): " + password1.equals(password3));  // true


        // ============================================
        // SECTION 9: CONVERTING BETWEEN STRINGS AND OTHER TYPES
        // (Recap from Type Casting - shown here in String context)
        // ============================================

        // Number to String
        int num = 100;
        String numStr = String.valueOf(num);

        // String to Number
        String numericInput = "250";
        int parsedNum = Integer.parseInt(numericInput);

        System.out.println("Number to String: " + numStr);
        System.out.println("String to Number: " + parsedNum);
    }
}