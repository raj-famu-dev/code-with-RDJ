// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
public class _6_ExceptionChaining {

    // A higher-level exception that can remember the lower-level cause
    static class ConfigException extends Exception {
        ConfigException(String message) {
            super(message);
        }

        ConfigException(String message, Throwable cause) {
            super(message, cause);              // the cause travels with the new exception
        }
    }

    // LOW level: throws a technical exception
    static int readPort(String text) {
        return Integer.parseInt(text);          // NumberFormatException
    }

    // HIGH level, the good way: translate AND keep the cause
    static int loadPortGood(String text) throws ConfigException {
        try {
            return readPort(text);
        } catch (NumberFormatException e) {
            throw new ConfigException("Invalid port setting: '" + text + "'", e);
        }
    }

    // HIGH level, the bad way: translate and THROW AWAY the cause
    static int loadPortBad(String text) throws ConfigException {
        try {
            return readPort(text);
        } catch (NumberFormatException e) {
            throw new ConfigException("Invalid port setting");     // the real reason is gone
        }
    }

    static void printCauseChain(Throwable t) {
        int level = 0;
        while (t != null) {
            System.out.println("  ".repeat(level) + "-> " + t.getClass().getSimpleName() + ": " + t.getMessage());
            t = t.getCause();
            level++;
        }
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHY CHAINING EXISTS
        // Each layer of a program speaks its own language. The file layer talks
        // about IOException, the config layer about "invalid setting". A higher
        // layer should translate the problem, but the original technical cause
        // is what you need to debug it. A chain keeps both.
        // ============================================


        // ============================================
        // SECTION 2: THE GOOD WAY - THE CAUSE IS PRESERVED
        // ============================================

        try {
            loadPortGood("80a");
        } catch (ConfigException e) {
            System.out.println("Good version:");
            printCauseChain(e);
            System.out.println("  getCause() is a " + e.getCause().getClass().getSimpleName());
        }


        // ============================================
        // SECTION 3: TRAP - LOSING THE CAUSE
        // Same failure, but the chain stops at the new exception. Nothing tells
        // you WHICH text failed to parse or why. This is a classic way to turn a
        // five-minute bug into a two-hour one.
        // ============================================

        try {
            loadPortBad("80a");
        } catch (ConfigException e) {
            System.out.println("Bad version:");
            printCauseChain(e);
            System.out.println("  getCause() is " + e.getCause());
        }


        // ============================================
        // SECTION 4: WRAPPING A CHECKED EXCEPTION IN AN UNCHECKED ONE
        // Useful when an interface does not allow 'throws'. Always pass the cause.
        // ============================================

        try {
            try {
                throw new java.io.IOException("socket closed");
            } catch (java.io.IOException e) {
                throw new RuntimeException("Could not complete request", e);
            }
        } catch (RuntimeException e) {
            System.out.println("Wrapped:");
            printCauseChain(e);
        }


        // ============================================
        // SECTION 5: RULES OF THUMB
        // - When you catch and throw a different exception, pass the original as the cause.
        // - Do not log AND rethrow at every layer (the same error appears many
        //   times in the logs). Pick one place to log, usually the top.
        // - printStackTrace() prints the whole chain with "Caused by:" lines.
        // ============================================
    }
}
