// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.List;

public class _4_SwitchExpressionsAndPatterns {

    enum Day { MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY }

    sealed interface Shape permits Circle, Rectangle { }

    record Circle(double radius) implements Shape { }

    record Rectangle(double width, double height) implements Shape { }

    record Point(int x, int y) { }

    record Line(Point from, Point to) { }

    // ============================================
    // SECTION 1: THE OLD switch STATEMENT AND ITS TRAPS
    // ============================================

    static int oldStyle(Day day) {
        int length;
        switch (day) {
            case MONDAY:
            case FRIDAY:
            case SUNDAY:
                length = 6;
                break;                                             // forget this 'break' and execution FALLS THROUGH
            case TUESDAY:
                length = 7;
                break;
            default:
                length = 8;
        }
        return length;
    }

    // ============================================
    // SECTION 2: switch AS AN EXPRESSION (Java 14)
    // It produces a VALUE. Arrow form: no fall-through, no 'break', several labels per case.
    // ============================================

    static int letters(Day day) {
        return switch (day) {
            case MONDAY, FRIDAY, SUNDAY -> 6;
            case TUESDAY -> 7;
            case THURSDAY, SATURDAY -> 8;
            case WEDNESDAY -> 9;                                   // an enum switch expression must cover ALL constants
        };
    }

    // A block with 'yield' when a case needs several statements
    static String describe(Day day) {
        return switch (day) {
            case SATURDAY, SUNDAY -> "weekend";
            default -> {
                String label = day.name().charAt(0) + day.name().substring(1).toLowerCase();
                yield label + " is a working day";                 // yield = "this is the value of this case"
            }
        };
    }

    // ============================================
    // SECTION 3: PATTERN MATCHING FOR instanceof (Java 16)
    // Test the type AND get a correctly typed variable in one step. No cast line.
    // ============================================

    static String oldInstanceof(Object o) {
        if (o instanceof String) {
            String s = (String) o;                                 // the repeated cast
            return "string of length " + s.length();
        }
        return "something else";
    }

    static String newInstanceof(Object o) {
        if (o instanceof String s && !s.isEmpty()) {               // 's' exists only where the test is known to be true
            return "string of length " + s.length();
        }
        return "something else";
    }

    // ============================================
    // SECTION 4: PATTERN MATCHING FOR switch (Java 21)
    // case Type name -> ...    with an optional guard:  case Type name when condition -> ...
    // Order matters: the FIRST matching case wins, so put specific cases before general ones.
    // ============================================

    static String classify(Object o) {
        return switch (o) {
            case null -> "null (handled explicitly, no NullPointerException)";
            case Integer i when i > 100 -> "big integer " + i;
            case Integer i -> "integer " + i;
            case String s when s.isBlank() -> "blank string";
            case String s -> "string \"" + s + "\"";
            case int[] arr -> "int array of length " + arr.length;
            case Day d -> "a day: " + d;
            default -> "something else: " + o.getClass().getSimpleName();
        };
    }
    // Swapping the two Integer cases would be a COMPILE ERROR ("this case label is dominated by a preceding one"):
    // the general case would swallow the specific one.

    static double area(Shape shape) {
        return switch (shape) {                                    // sealed: exhaustive without default
            case Circle c -> Math.PI * c.radius() * c.radius();
            case Rectangle r -> r.width() * r.height();
        };
    }

    // ============================================
    // SECTION 5: RECORD PATTERNS (Java 21) - TAKE THE OBJECT APART IN THE PATTERN
    // ============================================

    static String where(Object o) {
        return switch (o) {
            case Point(int x, int y) when x == 0 && y == 0 -> "the origin";
            case Point(int x, int y) -> "point at " + x + "," + y;
            case Line(Point(var x1, var y1), Point(var x2, var y2)) ->          // nested record patterns
                    "line of length " + String.format("%.2f", Math.hypot(x2 - x1, y2 - y1));
            default -> "not a geometry object";
        };
    }

    public static void main(String[] args) {

        System.out.println("old switch Monday = " + oldStyle(Day.MONDAY) + ", new switch Monday = " + letters(Day.MONDAY));
        boolean same = true;
        for (Day d : Day.values()) {
            same &= d.name().length() == letters(d);               // the numbers equal the number of letters in each name
        }
        System.out.println("letters() matches the real name lengths for all days: " + same);
        System.out.println(describe(Day.SUNDAY) + " / " + describe(Day.WEDNESDAY));

        System.out.println("--- instanceof ---");
        System.out.println(oldInstanceof("hello") + " / " + newInstanceof("hello") + " / " + newInstanceof(42));

        System.out.println("--- pattern switch ---");
        for (Object o : new Object[]{null, 7, 700, "  ", "hi", new int[]{1, 2}, Day.FRIDAY, 3.5}) {
            System.out.println(classify(o));
        }

        System.out.println("--- sealed shapes ---");
        List<Shape> shapes = List.of(new Circle(1), new Rectangle(2, 3));
        shapes.forEach(s -> System.out.printf("%.2f%n", area(s)));

        System.out.println("--- record patterns ---");
        System.out.println(where(new Point(0, 0)));
        System.out.println(where(new Point(3, 4)));
        System.out.println(where(new Line(new Point(0, 0), new Point(3, 4))));
        System.out.println(where("text"));

        // ============================================
        // SECTION 6: RULES TO REMEMBER
        // 1) Prefer arrow switches: no fall-through.
        // 2) A switch EXPRESSION must be exhaustive: cover every case or add default.
        //    Over a sealed type or an enum you can skip default and get compile-time safety.
        // 3) Put specific patterns (with 'when' guards) before general ones.
        // 4) 'case null' is available in pattern switches; without it, null throws NullPointerException.
        // 5) Do not reach for patterns when a simple method on the type would do:
        //    polymorphism (a method on each class) is still the right tool when YOU own the classes.
        // ============================================
    }
}
