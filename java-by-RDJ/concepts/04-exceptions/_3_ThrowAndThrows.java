// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.io.IOException;

public class _3_ThrowAndThrows {

    // 'throw' (no s) ACTIONS an exception: it creates the problem right here.
    // 'throws' (with s) DECLARES that a method may pass a checked exception to its caller.

    static void validateAge(int age) {
        if (age < 0) {
            throw new IllegalArgumentException("Age cannot be negative: " + age);    // unchecked: no 'throws' needed
        }
    }

    static void loadData() throws IOException {
        throw new IOException("disk not ready");        // checked: MUST be declared
    }

    // ---- three methods stacked on top of each other, to watch an exception travel ----

    static void methodC() {
        System.out.println("  methodC: about to fail");
        try {
            throw new IllegalStateException("something broke in C");
        } finally {
            System.out.println("  methodC: finally runs while the exception travels up");
        }
    }

    static void methodB() {
        System.out.println("  methodB: calling C");
        try {
            methodC();
            System.out.println("  methodB: this line is skipped");
        } finally {
            System.out.println("  methodB: finally runs too");
        }
    }

    static void methodA() {
        System.out.println("  methodA: calling B");
        try {
            methodB();
        } catch (IllegalStateException e) {
            System.out.println("  methodA: caught it -> " + e.getMessage());
        }
    }

    static void rethrowExample() throws IOException {
        try {
            loadData();
        } catch (IOException e) {
            System.out.println("  logging the problem, then letting the caller decide");
            throw e;                 // rethrow the SAME exception
        }
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: throw - CREATING AN EXCEPTION ON PURPOSE
        // Use it to reject invalid input early, with a clear message.
        // ============================================

        try {
            validateAge(-5);
        } catch (IllegalArgumentException e) {
            System.out.println("Caught: " + e.getMessage());
        }


        // ============================================
        // SECTION 2: throws - DECLARING A CHECKED EXCEPTION
        // The caller is now forced to catch it or declare it as well.
        // ============================================

        // loadData();       // COMPILE ERROR: unreported exception java.io.IOException
        try {
            loadData();
        } catch (IOException e) {
            System.out.println("Caught: " + e.getMessage());
        }


        // ============================================
        // SECTION 3: HOW AN EXCEPTION TRAVELS UP THE CALL STACK
        // If a method does not catch it, the exception leaves that method
        // immediately and goes to whoever called it, and so on, until some
        // method catches it or the program ends. 'finally' blocks run on the way.
        // ============================================

        System.out.println("Calling methodA:");
        methodA();
        System.out.println("Back in main, program continues normally.");


        // ============================================
        // SECTION 4: READING A STACK TRACE
        // getStackTrace() lists the call chain: innermost method first.
        // ============================================

        try {
            methodC();
        } catch (IllegalStateException e) {
            StackTraceElement top = e.getStackTrace()[0];
            System.out.println("Thrown inside method: " + top.getMethodName()
                    + ", called from: " + e.getStackTrace()[1].getMethodName());
        }


        // ============================================
        // SECTION 5: RETHROWING
        // Catch to do something (log, clean up), then throw it on so the
        // caller still finds out. Rethrow the original; do not hide it.
        // ============================================

        try {
            rethrowExample();
        } catch (IOException e) {
            System.out.println("Caller received the rethrown: " + e.getMessage());
        }


        // ============================================
        // SECTION 6: WHERE SHOULD YOU CATCH?
        // Catch where you can DO something useful: retry, show a message, use a
        // default. If you cannot, let it propagate. Catching too early and
        // doing nothing hides bugs.
        // ============================================
    }
}
