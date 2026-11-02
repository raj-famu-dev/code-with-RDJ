// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.io.BufferedReader;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.List;

/**
 * DECORATOR: add behaviour to an object by WRAPPING it in another object with the same interface.
 * PROBLEM  : you want optional extras in any combination (milk, sugar, logging, caching, compression).
 *            Using inheritance you would need a subclass for every combination:
 *            Coffee, CoffeeWithMilk, CoffeeWithSugar, CoffeeWithMilkAndSugar ... (an explosion).
 * SOLUTION : each extra is a small wrapper class that implements the same interface, holds the thing it wraps,
 *            and adds its bit before/after delegating. Wrappers stack in any order.
 * TRADE-OFF: many tiny classes; debugging goes through layers; order of wrappers can matter;
 *            and callers cannot tell which wrappers are present.
 */
public class _6_Decorator {

    // ============================================
    // EXAMPLE 1: COFFEE - the textbook case
    // ============================================

    interface Coffee {
        double cost();

        String description();
    }

    static class PlainCoffee implements Coffee {
        public double cost() {
            return 2.00;
        }

        public String description() {
            return "coffee";
        }
    }

    // the abstract decorator: IS a Coffee, HAS a Coffee
    static abstract class CoffeeDecorator implements Coffee {
        protected final Coffee inner;

        CoffeeDecorator(Coffee inner) {
            this.inner = inner;
        }
    }

    static class Milk extends CoffeeDecorator {
        Milk(Coffee inner) {
            super(inner);
        }

        public double cost() {
            return inner.cost() + 0.50;
        }

        public String description() {
            return inner.description() + " + milk";
        }
    }

    static class Sugar extends CoffeeDecorator {
        Sugar(Coffee inner) {
            super(inner);
        }

        public double cost() {
            return inner.cost() + 0.20;
        }

        public String description() {
            return inner.description() + " + sugar";
        }
    }

    static class Syrup extends CoffeeDecorator {
        Syrup(Coffee inner) {
            super(inner);
        }

        public double cost() {
            return inner.cost() + 0.75;
        }

        public String description() {
            return inner.description() + " + syrup";
        }
    }

    // ============================================
    // EXAMPLE 2: A MORE REALISTIC USE - cross-cutting behaviour around a service
    // ============================================

    interface PriceService {
        double priceOf(String item);
    }

    static class SlowPriceService implements PriceService {
        int realLookups = 0;

        public double priceOf(String item) {
            realLookups++;                                         // pretend this is a slow database/API call
            return item.length() * 1.5;
        }
    }

    static class LoggingPriceService implements PriceService {
        private final PriceService inner;
        final List<String> log = new ArrayList<>();

        LoggingPriceService(PriceService inner) {
            this.inner = inner;
        }

        public double priceOf(String item) {
            double result = inner.priceOf(item);
            log.add("priceOf(" + item + ") = " + result);
            return result;
        }
    }

    static class CachingPriceService implements PriceService {
        private final PriceService inner;
        private final java.util.Map<String, Double> cache = new java.util.HashMap<>();

        CachingPriceService(PriceService inner) {
            this.inner = inner;
        }

        public double priceOf(String item) {
            return cache.computeIfAbsent(item, inner::priceOf);
        }
    }

    public static void main(String[] args) throws Exception {

        System.out.println("--- coffee ---");
        Coffee plain = new PlainCoffee();
        Coffee fancy = new Syrup(new Milk(new Sugar(new Milk(new PlainCoffee()))));   // wrappers stack, even repeated ones
        for (Coffee c : List.of(plain, new Milk(plain), new Sugar(new Milk(plain)), fancy)) {
            System.out.printf("%-40s $%.2f%n", c.description(), c.cost());
        }

        System.out.println("--- services ---");
        SlowPriceService slow = new SlowPriceService();
        LoggingPriceService logging = new LoggingPriceService(slow);
        PriceService cachedAndLogged = new CachingPriceService(logging);   // cache OUTSIDE logging: hits never reach the log

        for (String item : List.of("apple", "apple", "banana", "apple")) {
            cachedAndLogged.priceOf(item);
        }
        System.out.println("4 calls made, real lookups: " + slow.realLookups + ", log: " + logging.log);

        // ORDER MATTERS: swap the wrappers and the log sees every call, including cache hits
        SlowPriceService slow2 = new SlowPriceService();
        CachingPriceService caching2 = new CachingPriceService(slow2);
        LoggingPriceService logging2 = new LoggingPriceService(caching2);   // logging OUTSIDE caching
        for (String item : List.of("apple", "apple", "banana", "apple")) {
            logging2.priceOf(item);
        }
        System.out.println("swapped order, real lookups: " + slow2.realLookups + ", log entries: " + logging2.log.size());

        System.out.println("--- decorators already in the JDK ---");
        // BufferedReader DECORATES any Reader by adding buffering and readLine()
        try (BufferedReader reader = new BufferedReader(new StringReader("line one\nline two"))) {
            System.out.println("BufferedReader(StringReader): " + reader.readLine() + " | " + reader.readLine());
        }
        // Collections.unmodifiableList(list) wraps a list so that writes throw
        List<String> wrapped = java.util.Collections.unmodifiableList(new ArrayList<>(List.of("x")));
        try {
            wrapped.add("y");
        } catch (UnsupportedOperationException e) {
            System.out.println("Collections.unmodifiableList decorates a List: add() -> UnsupportedOperationException");
        }

        // ============================================
        // WHEN IT MAKES THE CODE WORSE (exit-test material)
        // - Only ONE extra, never combined: a simple subclass or an if is clearer than a decorator hierarchy.
        // - When callers need to ask "is there milk in this coffee?": the wrappers hide their own types, and
        //   unwrapping with instanceof checks defeats the point. Model that as data instead.
        // - Deep stacks of decorators where the order silently changes behaviour (the cache/log example above).
        // ============================================
    }
}
