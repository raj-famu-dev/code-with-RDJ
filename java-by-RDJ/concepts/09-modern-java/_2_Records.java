// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;

public class _2_Records {

    // ============================================
    // SECTION 1: A RECORD IN ONE LINE
    // The class below is "a transparent holder of data". From the header alone, the compiler writes:
    //   - private final fields x and y
    //   - a constructor Point(int x, int y)
    //   - accessor methods x() and y()   (NOT getX())
    //   - equals(), hashCode() and toString() based on ALL the components
    // The same thing as a hand-written class would take about 30 lines.
    // ============================================

    record Point(int x, int y) { }

    // The old way, for comparison (what you used to write by hand)
    static final class OldPoint {
        private final int x;
        private final int y;

        OldPoint(int x, int y) {
            this.x = x;
            this.y = y;
        }

        int getX() {
            return x;
        }

        int getY() {
            return y;
        }

        @Override
        public boolean equals(Object o) {
            return o instanceof OldPoint p && p.x == x && p.y == y;
        }

        @Override
        public int hashCode() {
            return Objects.hash(x, y);
        }

        @Override
        public String toString() {
            return "OldPoint[x=" + x + ", y=" + y + "]";
        }
    }

    // ============================================
    // SECTION 2: COMPACT CONSTRUCTOR - VALIDATION AND NORMALIZATION
    // No parameter list, no field assignments: the compiler assigns the fields AFTER your code runs.
    // Reassigning a parameter changes what gets stored.
    // ============================================

    record Email(String address) {
        Email {
            Objects.requireNonNull(address, "address");
            address = address.trim().toLowerCase();                // normalize before it is stored
            if (!address.contains("@")) {
                throw new IllegalArgumentException("not an email: " + address);
            }
        }

        String domain() {                                          // records can have ordinary methods
            return address.substring(address.indexOf('@') + 1);
        }
    }

    // ============================================
    // SECTION 3: EXTRA STATIC FACTORIES, CONSTANTS, AND ALTERNATIVE CONSTRUCTORS
    // ============================================

    record Range(int low, int high) {
        static final Range EMPTY = new Range(0, 0);

        Range {
            if (low > high) {
                throw new IllegalArgumentException("low " + low + " > high " + high);
            }
        }

        Range(int single) {                                        // other constructors must delegate to the canonical one
            this(single, single);
        }

        static Range of(int a, int b) {                            // order-forgiving factory
            return new Range(Math.min(a, b), Math.max(a, b));
        }

        int length() {
            return high - low;
        }
    }

    // ============================================
    // SECTION 4: A SHALLOW-IMMUTABILITY TRAP
    // Fields are final, but a LIST in a record is still a mutable list.
    // Make a defensive copy in the compact constructor.
    // ============================================

    record LeakyTeam(String name, List<String> members) { }

    record SafeTeam(String name, List<String> members) {
        SafeTeam {
            members = List.copyOf(members);                        // unmodifiable copy, so outsiders cannot change it
        }
    }

    // ============================================
    // SECTION 5: RECORDS CAN IMPLEMENT INTERFACES AND BE GENERIC
    // ============================================

    interface Shape {
        double area();
    }

    record Circle(double radius) implements Shape {
        public double area() {
            return Math.PI * radius * radius;
        }
    }

    record Pair<A, B>(A first, B second) { }

    public static void main(String[] args) {

        // --- what you get for free ---
        Point p = new Point(3, 4);
        Point q = new Point(3, 4);
        System.out.println("toString:  " + p);
        System.out.println("accessors: x() = " + p.x() + ", y() = " + p.y());
        System.out.println("equals:    " + p.equals(q) + ", same object: " + (p == q));
        System.out.println("hashCode equal: " + (p.hashCode() == q.hashCode()));
        System.out.println("old-style class has the same behaviour: "
                + new OldPoint(3, 4).equals(new OldPoint(3, 4)) + ", " + new OldPoint(3, 4));

        // --- compact constructor ---
        Email email = new Email("  Ada@Example.COM ");
        System.out.println("normalized email: " + email + ", domain: " + email.domain());
        try {
            new Email("nonsense");
        } catch (IllegalArgumentException e) {
            System.out.println("validation: " + e.getMessage());
        }

        // --- range ---
        System.out.println("Range.of(9, 2) = " + Range.of(9, 2) + ", length " + Range.of(9, 2).length()
                + ", single = " + new Range(5) + ", EMPTY = " + Range.EMPTY);
        try {
            new Range(5, 1);
        } catch (IllegalArgumentException e) {
            System.out.println("validation: " + e.getMessage());
        }

        // --- shallow immutability ---
        List<String> names = new ArrayList<>(List.of("Ada", "Linus"));
        LeakyTeam leaky = new LeakyTeam("leaky", names);
        SafeTeam safe = new SafeTeam("safe", names);
        names.add("Intruder");                                     // changes the caller's list afterwards
        System.out.println("leaky team members: " + leaky.members());
        System.out.println("safe team members:  " + safe.members());
        try {
            safe.members().add("x");
        } catch (UnsupportedOperationException e) {
            System.out.println("safe team list cannot be modified: UnsupportedOperationException");
        }

        // --- interface, generics, local records ---
        System.out.printf("circle area: %.2f%n", new Circle(2).area());
        Pair<String, Integer> pair = new Pair<>("age", 30);
        System.out.println("generic record: " + pair);

        record Score(String player, int points) { }                // a LOCAL record: handy inside one method
        List<Score> scores = List.of(new Score("ada", 90), new Score("linus", 75), new Score("grace", 99));
        System.out.println("best score: " + scores.stream().max(Comparator.comparingInt(Score::points)).get());

        // ============================================
        // SECTION 6: WHAT A RECORD CANNOT DO (AND WHEN NOT TO USE ONE)
        // - cannot extend another class (it implicitly extends java.lang.Record); it is implicitly final
        // - cannot declare extra INSTANCE fields (all state is in the header)
        // - fields cannot be reassigned: there are no setters
        // Not a good fit for: JPA entities (need mutability and no-arg constructors),
        // or classes with identity-based behaviour (two accounts with equal fields are NOT the same account).
        // ============================================
    }
}
