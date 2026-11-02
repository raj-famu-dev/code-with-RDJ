// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
public class _7_FinallyGotchas {

    // Gotcha 1: 'finally' runs even when the try block has already hit 'return'
    static String returnInTry() {
        try {
            System.out.println("  try: about to return");
            return "value from try";
        } finally {
            System.out.println("  finally: runs BEFORE the method actually returns");
        }
    }

    // Gotcha 2: the return value is fixed BEFORE finally runs (for primitives)
    static int primitiveReturn() {
        int x = 1;
        try {
            return x;               // value 1 is remembered here
        } finally {
            x = 99;                 // changes the variable, NOT the already-remembered return value
        }
    }

    // Gotcha 3: ...but for a MUTABLE OBJECT, finally can still change what the caller sees
    static StringBuilder objectReturn() {
        StringBuilder sb = new StringBuilder("hello");
        try {
            return sb;              // the reference is remembered
        } finally {
            sb.append(" (changed in finally)");     // same object, so the caller sees this
        }
    }

    // Gotcha 4: a 'return' in finally SWALLOWS an exception (BAD, never do this)
    @SuppressWarnings("finally")
    static String returnInFinallyHidesException() {
        try {
            throw new IllegalStateException("important error");
        } finally {
            return "finally wins, exception vanished";
        }
    }

    // Gotcha 5: an exception thrown in finally REPLACES the original
    static void exceptionInFinally() {
        try {
            throw new IllegalStateException("original problem");
        } finally {
            throw new IllegalArgumentException("problem from finally");
        }
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: finally ALWAYS RUNS
        // Even if the try block returns, throws, or breaks out of a loop.
        // ============================================

        System.out.println("Gotcha 1:");
        System.out.println("  got: " + returnInTry());


        // ============================================
        // SECTION 2: PRIMITIVE RETURN VALUE IS FIXED EARLY
        // ============================================

        System.out.println("Gotcha 2: primitiveReturn() = " + primitiveReturn() + "   (not 99)");


        // ============================================
        // SECTION 3: A MUTABLE OBJECT CAN STILL BE CHANGED
        // The reference was remembered, but it points at an object that finally modifies.
        // ============================================

        System.out.println("Gotcha 3: objectReturn() = " + objectReturn());


        // ============================================
        // SECTION 4: return IN finally HIDES EXCEPTIONS
        // The IllegalStateException is thrown, then discarded when finally
        // returns normally. A real error disappears without a trace.
        // The compiler can warn about it with: javac -Xlint:finally
        // ============================================

        System.out.println("Gotcha 4: " + returnInFinallyHidesException());


        // ============================================
        // SECTION 5: AN EXCEPTION IN finally REPLACES THE ORIGINAL
        // The caller only sees the second exception. The first one is lost
        // (try-with-resources avoids this by suppressing, see _5).
        // ============================================

        try {
            exceptionInFinally();
        } catch (RuntimeException e) {
            System.out.println("Gotcha 5: caller saw '" + e.getMessage() + "', original was lost");
        }


        // ============================================
        // SECTION 6: THE ONE THING THAT SKIPS finally
        // System.exit(0) stops the JVM immediately; finally does not run.
        // (A crash of the JVM or killing the process also skips it.)
        // Not run here, because it would end this program.
        // ============================================


        // ============================================
        // SECTION 7: HOW TO USE finally WELL
        // - Keep it short and only for cleanup.
        // - Never return or throw from it.
        // - For closing resources, prefer try-with-resources.
        // ============================================
    }
}
