// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.ArrayList;
import java.util.List;

/**
 * SOLID: five design guidelines. For each one: a VIOLATION, then the FIX.
 * All helper types are nested so the whole folder compiles together.
 */
public class _1_SolidPrinciples {

    // ============================================
    // S - SINGLE RESPONSIBILITY: a class should have ONE reason to change
    // ============================================

    // VIOLATION: three reasons to change (business rule, storage format, presentation)
    static class BadReport {
        double total(List<Double> amounts) {
            double sum = 0;
            for (double a : amounts) sum += a;
            return sum;
        }

        String toCsv(List<Double> amounts) {                       // formatting is another job
            StringBuilder sb = new StringBuilder();
            for (double a : amounts) sb.append(a).append(',');
            return sb.toString();
        }

        void save(String text) {                                   // and so is storage
            System.out.println("  (saving to disk) " + text);
        }
    }

    // FIX: one job per class
    static class Calculator {
        double total(List<Double> amounts) {
            return amounts.stream().mapToDouble(Double::doubleValue).sum();
        }
    }

    static class CsvFormatter {
        String format(List<Double> amounts) {
            StringBuilder sb = new StringBuilder();
            for (double a : amounts) sb.append(a).append(',');
            return sb.toString();
        }
    }

    static class Storage {
        void save(String text) {
            System.out.println("  (saving to disk) " + text);
        }
    }

    // ============================================
    // O - OPEN/CLOSED: open for EXTENSION, closed for MODIFICATION
    // ============================================

    // VIOLATION: every new shape means editing this method (and risking old code)
    static class BadAreaCalculator {
        double area(String kind, double a, double b) {
            if (kind.equals("circle")) return Math.PI * a * a;
            if (kind.equals("rectangle")) return a * b;
            throw new IllegalArgumentException("unknown shape " + kind);   // a new shape = edit here
        }
    }

    // FIX: new shapes are NEW classes; the calculator never changes
    interface Shape {
        double area();
    }

    record Circle(double radius) implements Shape {
        public double area() {
            return Math.PI * radius * radius;
        }
    }

    record Rectangle(double w, double h) implements Shape {
        public double area() {
            return w * h;
        }
    }

    record Square(double side) implements Shape {                  // added later, nothing else was edited
        public double area() {
            return side * side;
        }
    }

    static double totalArea(List<Shape> shapes) {
        return shapes.stream().mapToDouble(Shape::area).sum();
    }

    // ============================================
    // L - LISKOV SUBSTITUTION: a subtype must work wherever its parent is expected
    // ============================================

    // VIOLATION: the classic "a Square is a Rectangle" trap
    static class MutableRectangle {
        protected int width;
        protected int height;

        void setWidth(int w) {
            this.width = w;
        }

        void setHeight(int h) {
            this.height = h;
        }

        int area() {
            return width * height;
        }
    }

    static class MutableSquare extends MutableRectangle {
        @Override
        void setWidth(int w) {
            this.width = w;
            this.height = w;                                       // surprise: changes the height too
        }

        @Override
        void setHeight(int h) {
            this.width = h;
            this.height = h;
        }
    }

    static int stretchAndMeasure(MutableRectangle r) {             // code written for ANY rectangle
        r.setWidth(5);
        r.setHeight(2);
        return r.area();                                           // a rectangle 5 wide and 2 high is 10
    }

    // FIX: do not force the inheritance. Shape (above) lets Square stand on its own with the same contract.

    // ============================================
    // I - INTERFACE SEGREGATION: do not force classes to implement methods they do not need
    // ============================================

    // VIOLATION: a fat interface
    interface FatWorker {
        void work();

        void eat();
    }

    static class Robot implements FatWorker {
        public void work() {
            System.out.println("  robot works");
        }

        public void eat() {
            throw new UnsupportedOperationException("robots do not eat");   // forced to implement nonsense
        }
    }

    // FIX: small, focused interfaces
    interface Workable {
        void work();
    }

    interface Eatable {
        void eat();
    }

    static class SlimRobot implements Workable {
        public void work() {
            System.out.println("  slim robot works");
        }
    }

    static class Human implements Workable, Eatable {
        public void work() {
            System.out.println("  human works");
        }

        public void eat() {
            System.out.println("  human eats");
        }
    }

    // ============================================
    // D - DEPENDENCY INVERSION: depend on ABSTRACTIONS, not on concrete classes
    // ============================================

    // VIOLATION: the high-level class builds its own low-level dependency
    static class SmsSender {
        void send(String msg) {
            System.out.println("  SMS: " + msg);
        }
    }

    static class BadAlertService {
        private final SmsSender sender = new SmsSender();          // welded to SMS; cannot test, cannot swap
        void alert(String msg) {
            sender.send(msg);
        }
    }

    // FIX: depend on an interface and PASS the dependency in ("dependency injection")
    interface MessageSender {
        void send(String msg);
    }

    static class EmailSender implements MessageSender {
        public void send(String msg) {
            System.out.println("  EMAIL: " + msg);
        }
    }

    static class FakeSender implements MessageSender {             // a test double: easy now
        final List<String> sent = new ArrayList<>();

        public void send(String msg) {
            sent.add(msg);
        }
    }

    static class AlertService {
        private final MessageSender sender;

        AlertService(MessageSender sender) {                       // injected
            this.sender = sender;
        }

        void alert(String msg) {
            sender.send(msg);
        }
    }

    public static void main(String[] args) {

        System.out.println("--- S: single responsibility ---");
        List<Double> amounts = List.of(10.0, 20.5);
        System.out.println("bad class does everything: total = " + new BadReport().total(amounts));
        Calculator calc = new Calculator();
        new Storage().save(new CsvFormatter().format(amounts) + " total=" + calc.total(amounts));

        System.out.println("--- O: open/closed ---");
        System.out.printf("old: circle %.2f%n", new BadAreaCalculator().area("circle", 1, 0));
        List<Shape> shapes = List.of(new Circle(1), new Rectangle(2, 3), new Square(2));
        System.out.printf("new: total area with a Square added later = %.2f%n", totalArea(shapes));

        System.out.println("--- L: Liskov substitution ---");
        System.out.println("MutableRectangle gives " + stretchAndMeasure(new MutableRectangle()) + " (expected 10)");
        System.out.println("MutableSquare gives    " + stretchAndMeasure(new MutableSquare()) + " (expected 10: the 'subtype' broke the contract)");

        System.out.println("--- I: interface segregation ---");
        try {
            new Robot().eat();
        } catch (UnsupportedOperationException e) {
            System.out.println("  fat interface forced a lie: " + e.getMessage());
        }
        new SlimRobot().work();
        Human human = new Human();
        human.work();
        human.eat();

        System.out.println("--- D: dependency inversion ---");
        new BadAlertService().alert("disk almost full");
        new AlertService(new EmailSender()).alert("disk almost full");
        FakeSender fake = new FakeSender();
        new AlertService(fake).alert("test alert");
        System.out.println("  test captured: " + fake.sent);

        // ============================================
        // WHEN SOLID MAKES CODE WORSE (exit-test material)
        // - Splitting a 10-line class into five tiny ones "for SRP" just to scatter the logic.
        // - Adding an interface for a class that will only ever have ONE implementation.
        // - Designing for extension that never arrives (O/C applied to code that never changes).
        // SOLID are guidelines for managing CHANGE. If nothing will change, they add cost for no benefit.
        // ============================================
    }
}
