// Tags: #Java #Exceptions #ExceptionsCapstone | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.List;

public class _8_ExceptionsCapstone {

    // ---- exception hierarchy: ONE parent so callers can catch "any validation problem" ----

    static class ValidationException extends Exception {
        private final String field;

        ValidationException(String field, String message) {
            super(field + ": " + message);
            this.field = field;
        }

        ValidationException(String field, String message, Throwable cause) {
            super(field + ": " + message, cause);
            this.field = field;
        }

        String getField() {
            return field;
        }
    }

    static class MissingFieldException extends ValidationException {
        MissingFieldException(String field) {
            super(field, "is required");
        }
    }

    static class InvalidFormatException extends ValidationException {
        InvalidFormatException(String field, String message, Throwable cause) {
            super(field, message, cause);
        }
    }

    static class OutOfRangeException extends ValidationException {
        OutOfRangeException(String field, int value, int min, int max) {
            super(field, "value " + value + " must be between " + min + " and " + max);
        }
    }

    record Person(String name, int age, String email) {
    }

    // ---- the validating step: it THROWS, it does not decide what to do about it ----

    static Person parse(String line) throws ValidationException {
        String[] parts = line.split(",", -1);
        if (parts.length != 3) {
            throw new ValidationException("record", "expected 3 fields but found " + parts.length);
        }

        String name = parts[0].trim();
        if (name.isEmpty()) throw new MissingFieldException("name");

        int age;
        try {
            age = Integer.parseInt(parts[1].trim());
        } catch (NumberFormatException e) {
            throw new InvalidFormatException("age", "'" + parts[1].trim() + "' is not a whole number", e);
        }
        if (age < 0 || age > 120) throw new OutOfRangeException("age", age, 0, 120);

        String email = parts[2].trim();
        if (!email.contains("@")) {
            throw new ValidationException("email", "'" + email + "' is missing '@'");
        }
        return new Person(name, age, email);
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THE INPUT
        // Hard-coded, so the program is predictable. Some lines are deliberately bad.
        // ============================================

        List<String> rawLines = List.of(
                "Ava,30,ava@example.com",
                "Ben,abc,ben@example.com",
                ",25,nobody@example.com",
                "Cleo,200,cleo@example.com",
                "Dev,41,dev-at-example.com",
                "Eli,28",
                "Fay,35,fay@example.com");


        // ============================================
        // SECTION 2: WHERE TO CATCH - AT THE BOUNDARY
        // parse() reports problems but cannot decide what to DO about them.
        // The loop is the place that can: skip the bad line, record the reason,
        // keep going. One bad record must not crash the whole batch.
        // ============================================

        List<Person> accepted = new ArrayList<>();
        List<String> rejected = new ArrayList<>();

        int lineNumber = 0;
        for (String line : rawLines) {
            lineNumber++;
            try {
                accepted.add(parse(line));
            } catch (OutOfRangeException e) {
                rejected.add("line " + lineNumber + " [range]  " + e.getMessage());
            } catch (InvalidFormatException e) {
                // the original NumberFormatException is still available as e.getCause()
                rejected.add("line " + lineNumber + " [format] " + e.getMessage()
                        + " (cause: " + e.getCause().getClass().getSimpleName() + ")");
            } catch (ValidationException e) {
                // handles MissingFieldException and the generic ones via the parent type
                rejected.add("line " + lineNumber + " [other]  " + e.getMessage());
            }
        }


        // ============================================
        // SECTION 3: THE REPORT
        // ============================================

        System.out.println("Accepted " + accepted.size() + " of " + rawLines.size() + " records:");
        accepted.forEach(p -> System.out.println("  " + p));

        System.out.println("Rejected " + rejected.size() + ":");
        rejected.forEach(r -> System.out.println("  " + r));


        // ============================================
        // SECTION 4: WHAT THIS FILE PUTS TOGETHER
        // - custom hierarchy with a shared parent (from _4)
        // - throw early with clear messages (from _3)
        // - chaining the NumberFormatException as the cause (from _6)
        // - catch ORDER: specific subclasses before the parent (from _1)
        // - catching at the boundary that can recover, not deep inside parse()
        // ============================================
    }
}
