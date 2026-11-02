// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class _2_CheckedVsUnchecked {

    // A method that can fail with a CHECKED exception must declare it with 'throws'
    static String readFirstLine(String pathText) throws IOException {
        return Files.readAllLines(Path.of(pathText)).get(0);
    }

    // Unchecked exceptions need no declaration
    static int parseAge(String text) {
        return Integer.parseInt(text);      // may throw NumberFormatException, no 'throws' needed
    }

    static int recurseForever(int depth) {
        return recurseForever(depth + 1) + 1;
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THE FAMILY TREE
        // Throwable
        //   |-- Error                      (JVM-level problems: OutOfMemoryError, StackOverflowError)
        //   |-- Exception                  (problems your program may reasonably handle)
        //         |-- IOException, SQLException, ...     CHECKED
        //         |-- RuntimeException                    UNCHECKED
        //               |-- NullPointerException, IllegalArgumentException,
        //                   ArithmeticException, IndexOutOfBoundsException, ...
        //
        // CHECKED   = Exception and its subclasses, EXCEPT RuntimeException branch.
        // UNCHECKED = RuntimeException and its subclasses, plus Error.
        // ============================================

        System.out.println("IOException is a checked Exception:        " + (Exception.class.isAssignableFrom(IOException.class)
                && !RuntimeException.class.isAssignableFrom(IOException.class)));
        System.out.println("NumberFormatException is unchecked:        " + RuntimeException.class.isAssignableFrom(NumberFormatException.class));


        // ============================================
        // SECTION 2: WHAT THE COMPILER ENFORCES FOR CHECKED EXCEPTIONS
        // You must either CATCH it or DECLARE it with 'throws'.
        // ============================================

        // String line = readFirstLine("missing.txt");     // COMPILE ERROR: unreported exception IOException

        try {
            String line = readFirstLine("this-file-does-not-exist.txt");
            System.out.println(line);
        } catch (IOException e) {
            System.out.println("Caught checked IOException: " + e.getClass().getSimpleName());
        }


        // ============================================
        // SECTION 3: UNCHECKED EXCEPTIONS - THE COMPILER STAYS QUIET
        // These usually signal a BUG in the calling code (null where it should
        // not be, a bad argument, an index off the end). You fix the code
        // instead of writing a handler for each one.
        // ============================================

        try {
            parseAge("twenty");
        } catch (NumberFormatException e) {
            System.out.println("Caught unchecked NumberFormatException: " + e.getMessage());
        }

        String text = null;
        try {
            text.length();
        } catch (NullPointerException e) {
            System.out.println("Caught unchecked NullPointerException");
        }


        // ============================================
        // SECTION 4: Error - NOT FOR YOUR PROGRAM TO HANDLE
        // Errors mean the JVM itself is in trouble. Catching one here is only to
        // SHOW it exists; real code should not try to recover from them.
        // ============================================

        try {
            recurseForever(0);
        } catch (StackOverflowError e) {
            System.out.println("Caught StackOverflowError (an Error, not an Exception)");
        }


        // ============================================
        // SECTION 5: WHY JAVA DRAWS THE LINE HERE
        // Checked   : the failure is outside the program's control but the caller
        //             can plausibly recover (file missing, network down, bad SQL).
        //             The compiler forces you to think about it.
        // Unchecked : the failure is a programming mistake. Forcing every call
        //             to handle it would bury the code in try/catch.
        // Debate: many modern libraries prefer unchecked exceptions because
        // checked ones spread 'throws' clauses through every layer.
        // ============================================


        // ============================================
        // SECTION 6: QUICK TEST
        // Is it checked or unchecked?
        //   FileNotFoundException   -> checked (extends IOException)
        //   ClassCastException      -> unchecked
        //   Exception (itself)      -> checked
        //   RuntimeException (itself) -> unchecked
        // ============================================
    }
}
