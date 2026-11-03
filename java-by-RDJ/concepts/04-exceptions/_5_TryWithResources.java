// Tags: #Java #Exceptions #TryResources | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.Arrays;

public class _5_TryWithResources {

    // Anything that implements AutoCloseable can go in a try-with-resources header
    static class Resource implements AutoCloseable {
        private final String name;
        private final boolean failOnClose;

        Resource(String name, boolean failOnClose) {
            this.name = name;
            this.failOnClose = failOnClose;
            System.out.println("  open  " + name);
        }

        void use(boolean fail) {
            System.out.println("  using " + name);
            if (fail) throw new IllegalStateException("body failed using " + name);
        }

        @Override
        public void close() {
            System.out.println("  close " + name);
            if (failOnClose) throw new IllegalArgumentException("close failed for " + name);
        }
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THE OLD WAY - AND WHY IT IS EASY TO GET WRONG
        // You must remember the finally block, null checks, and the fact that
        // close() itself can throw.
        // ============================================

        Resource old = null;
        try {
            old = new Resource("old-style", false);
            old.use(false);
        } finally {
            if (old != null) {
                old.close();
            }
        }


        // ============================================
        // SECTION 2: try-with-resources - CLOSING IS AUTOMATIC
        // The resource is closed when the block ends, whether it finished
        // normally or threw.
        // ============================================

        System.out.println("Section 2:");
        try (Resource r = new Resource("file", false)) {
            r.use(false);
        }


        // ============================================
        // SECTION 3: CLOSE HAPPENS EVEN WHEN THE BODY THROWS
        // ============================================

        System.out.println("Section 3:");
        try (Resource r = new Resource("db-connection", false)) {
            r.use(true);
        } catch (IllegalStateException e) {
            System.out.println("  caught: " + e.getMessage() + "   (resource was already closed)");
        }


        // ============================================
        // SECTION 4: SEVERAL RESOURCES CLOSE IN REVERSE ORDER
        // Last opened, first closed - like stacking and unstacking plates.
        // ============================================

        System.out.println("Section 4:");
        try (Resource first = new Resource("A", false);
             Resource second = new Resource("B", false)) {
            first.use(false);
            second.use(false);
        }


        // ============================================
        // SECTION 5: SUPPRESSED EXCEPTIONS
        // If the body throws AND close() throws, which one do you see?
        // The BODY exception is the one thrown. The close() exception is not
        // lost: it is attached to it as a "suppressed" exception.
        // (With the old finally style, the close() failure would REPLACE the
        // original, hiding the real cause.)
        // ============================================

        System.out.println("Section 5:");
        try (Resource r = new Resource("fragile", true)) {
            r.use(true);
        } catch (IllegalStateException e) {
            System.out.println("  primary:    " + e.getMessage());
            System.out.println("  suppressed: " + Arrays.toString(e.getSuppressed()));
        }


        // ============================================
        // SECTION 6: THE RESOURCE'S SCOPE
        // The variable exists only inside the try block (and is effectively
        // final). It is already closed by the time catch/finally run.
        // ============================================

        // try (Resource r = new Resource("x", false)) { }
        // r.use(false);     // COMPILE ERROR: r is out of scope here


        // ============================================
        // SECTION 7: WHAT YOU WILL USE IT FOR
        // Files, streams, database connections, sockets, scanners over files:
        // anything that must be released. You will use it in 07-file-io and
        // 10-jdbc-sql.
        // ============================================
    }
}
