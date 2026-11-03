// Tags: #Java #DesignPatterns #SOLID #Strategy | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

/**
 * STRATEGY: make an algorithm swappable by putting each version behind a common interface.
 * PROBLEM  : a class contains an if/else (or switch) that picks between several ways of doing the same job
 *            (shipping cost, discount, sorting). Adding a way means editing that class.
 * SOLUTION : each way becomes a small object implementing one interface; the class receives the one it should use.
 * TRADE-OFF: more types; callers must choose a strategy. In Java a strategy with ONE method is just a
 *            functional interface, so a lambda is often all you need (no class at all).
 */
public class _7_Strategy {

    // ============================================
    // BEFORE: the algorithm is hard-wired inside the class
    // ============================================

    static class BadShop {
        double shipping(String method, double kg) {
            if (method.equals("standard")) return 4.00 + kg * 0.5;
            if (method.equals("express")) return 10.00 + kg * 1.2;
            if (method.equals("pickup")) return 0;
            throw new IllegalArgumentException("unknown method " + method);    // new method = edit here
        }
    }

    // ============================================
    // AFTER: one interface, one small class per algorithm
    // ============================================

    @FunctionalInterface
    interface ShippingStrategy {
        double cost(double kg);
    }

    static class Standard implements ShippingStrategy {
        public double cost(double kg) {
            return 4.00 + kg * 0.5;
        }
    }

    static class Express implements ShippingStrategy {
        public double cost(double kg) {
            return 10.00 + kg * 1.2;
        }
    }

    // the CONTEXT: uses a strategy without knowing which one
    static class Order {
        private final double weightKg;
        private ShippingStrategy shipping;

        Order(double weightKg, ShippingStrategy shipping) {
            this.weightKg = weightKg;
            this.shipping = shipping;
        }

        void changeShipping(ShippingStrategy shipping) {           // strategies can be swapped at RUNTIME
            this.shipping = shipping;
        }

        double shippingCost() {
            return shipping.cost(weightKg);
        }
    }

    // ============================================
    // BECAUSE IT IS A FUNCTIONAL INTERFACE: lambdas and method references ARE strategies
    // ============================================

    static final ShippingStrategy PICKUP = kg -> 0;
    static final ShippingStrategy FLAT_RATE = kg -> 7.50;

    // ============================================
    // A SECOND EXAMPLE FROM THE JDK: Comparator IS the Strategy pattern
    // list.sort(strategy) - the algorithm (the sort) is fixed, the COMPARISON is the strategy.
    // ============================================

    record Product(String name, double price, int stock) { }

    // ============================================
    // A THIRD: choosing a strategy by name from a map (replaces the if/else completely)
    // ============================================

    static final Map<String, ShippingStrategy> BY_NAME = Map.of(
            "standard", new Standard(),
            "express", new Express(),
            "pickup", PICKUP,
            "flat", FLAT_RATE);

    public static void main(String[] args) {

        System.out.println("--- before ---");
        System.out.printf("BadShop standard 3kg: %.2f%n", new BadShop().shipping("standard", 3));

        System.out.println("--- strategy classes ---");
        Order order = new Order(3, new Standard());
        System.out.printf("standard: %.2f%n", order.shippingCost());
        order.changeShipping(new Express());
        System.out.printf("express:  %.2f   (swapped at runtime)%n", order.shippingCost());

        System.out.println("--- strategies as lambdas ---");
        order.changeShipping(PICKUP);
        System.out.printf("pickup:   %.2f%n", order.shippingCost());
        order.changeShipping(kg -> kg > 5 ? 0 : 3.99);             // a one-off strategy, written inline
        System.out.printf("inline:   %.2f   (free over 5 kg, otherwise 3.99)%n", order.shippingCost());

        System.out.println("--- Comparator is a strategy ---");
        List<Product> products = new ArrayList<>(List.of(
                new Product("lamp", 25.0, 4), new Product("desk", 180.0, 0), new Product("pen", 1.5, 300)));
        products.sort(Comparator.comparingDouble(Product::price));
        System.out.println("by price:       " + products.stream().map(Product::name).toList());
        products.sort(Comparator.comparingInt(Product::stock).reversed());
        System.out.println("by stock (desc): " + products.stream().map(Product::name).toList());

        System.out.println("--- choosing by name ---");
        for (String name : List.of("standard", "express", "pickup", "flat")) {
            System.out.printf("%-9s 2 kg: %5.2f%n", name, BY_NAME.get(name).cost(2));
        }

        // ============================================
        // WHEN IT MAKES THE CODE WORSE (exit-test material)
        // - Only two options that will never grow: an if/else is shorter and clearer.
        // - A strategy interface with one implementation "in case we need another later".
        // - Strategies that need to share lots of state with the context: you end up passing the whole
        //   context in, and the "separate" classes are tangled with it anyway.
        // ============================================
    }
}
