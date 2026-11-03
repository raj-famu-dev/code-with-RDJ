// Tags: #Java #ModernJava #SealedClasses | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.List;

public class _3_SealedClasses {

    // ============================================
    // SECTION 1: THE PROBLEM
    // A normal interface can be implemented by ANYONE, anywhere. If you write
    // "a Shape is a Circle, a Square or a Rectangle", nothing stops a stranger from adding a
    // fourth kind your code has never heard of.
    // ============================================

    // ============================================
    // SECTION 2: sealed ... permits - A CLOSED FAMILY
    // Only the listed types may extend/implement. Every permitted subtype MUST be
    // final, sealed, or non-sealed (a deliberate choice of how open it stays).
    // ============================================

    sealed interface Shape permits Circle, Rectangle, Triangle { }

    record Circle(double radius) implements Shape { }              // records are implicitly final: allowed

    record Rectangle(double width, double height) implements Shape { }

    static final class Triangle implements Shape {                 // 'final': no further subclasses
        final double base;
        final double height;

        Triangle(double base, double height) {
            this.base = base;
            this.height = height;
        }
    }

    // ============================================
    // SECTION 3: THE REWARD - EXHAUSTIVE switch
    // Because the compiler knows EVERY possible subtype, a switch over a sealed type
    // needs no default. Add a fourth shape later and every switch that forgot it
    // stops COMPILING: bugs move from runtime to compile time.
    // ============================================

    static double area(Shape shape) {
        return switch (shape) {
            case Circle c -> Math.PI * c.radius() * c.radius();
            case Rectangle r -> r.width() * r.height();
            case Triangle t -> 0.5 * t.base * t.height;
            // no default needed
        };
    }

    // ============================================
    // SECTION 4: THE THREE CHOICES FOR A PERMITTED SUBCLASS
    //   final       : the end of the line
    //   sealed      : opens another closed family below it
    //   non-sealed  : deliberately re-opens: anyone may extend THIS branch
    // ============================================

    sealed interface Vehicle permits Car, Truck, Custom { }

    record Car(int seats) implements Vehicle { }                   // final (record)

    sealed interface Truck extends Vehicle permits PickUp, Lorry { }   // a family inside the family

    record PickUp(double loadTons) implements Truck { }

    record Lorry(int axles) implements Truck { }

    non-sealed interface Custom extends Vehicle { }                // open: anyone may implement Custom

    record Hovercraft() implements Custom { }                      // allowed because Custom is non-sealed

    static String describe(Vehicle v) {
        return switch (v) {
            case Car c -> "car with " + c.seats() + " seats";
            case PickUp p -> "pick-up, " + p.loadTons() + " t";
            case Lorry l -> "lorry with " + l.axles() + " axles";
            case Custom c -> "custom vehicle " + c.getClass().getSimpleName();   // must cover the open branch
        };
    }

    // ============================================
    // SECTION 5: A CLASSIC USE - A "RESULT" THAT IS EITHER SUCCESS OR FAILURE
    // Instead of exceptions or nulls, the type says which cases exist.
    // ============================================

    sealed interface Result<T> permits Success, Failure { }

    record Success<T>(T value) implements Result<T> { }

    record Failure<T>(String reason) implements Result<T> { }

    static Result<Integer> parse(String text) {
        try {
            return new Success<>(Integer.parseInt(text));
        } catch (NumberFormatException e) {
            return new Failure<>("'" + text + "' is not a number");
        }
    }

    static String show(Result<Integer> r) {
        return switch (r) {
            case Success<Integer> s -> "ok: " + s.value();
            case Failure<Integer> f -> "failed: " + f.reason();
        };
    }

    public static void main(String[] args) {

        List<Shape> shapes = List.of(new Circle(1), new Rectangle(2, 3), new Triangle(4, 5));
        for (Shape s : shapes) {
            System.out.printf("%-10s area = %.2f%n", s.getClass().getSimpleName(), area(s));
        }

        System.out.println("--- the three choices ---");
        List<Vehicle> vehicles = List.of(new Car(5), new PickUp(1.5), new Lorry(3), new Hovercraft());
        vehicles.forEach(v -> System.out.println(describe(v)));

        System.out.println("--- Result as a sealed type ---");
        System.out.println(show(parse("42")));
        System.out.println(show(parse("forty-two")));

        // What the compiler refuses (kept as comments):
        // record Hexagon() implements Shape { }       // COMPILE ERROR: Hexagon is not listed in 'permits'
        // sealed interface Broken permits Foo { }     // COMPILE ERROR if Foo does not extend/implement Broken
        // In a switch, deleting the Triangle case makes the switch non-exhaustive: COMPILE ERROR.

        // ============================================
        // SECTION 6: RULES TO REMEMBER
        // 1) Permitted subclasses must be in the same module (or same package if no modules).
        //    In a single file they can be nested, and 'permits' can even be omitted.
        // 2) Each permitted subtype must declare final, sealed or non-sealed. Records and enums are implicitly final.
        // 3) Sealed + records + switch patterns = "algebraic data types", the modern Java way
        //    to model "one of these exact cases".
        // 4) Use it when the set of cases is truly fixed. For open-ended extension, use a normal interface.
        // ============================================
    }
}
