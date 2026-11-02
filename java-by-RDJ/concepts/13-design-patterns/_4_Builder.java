// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/**
 * BUILDER: construct a complex object step by step, with named steps and validation at the end.
 * PROBLEM  : a constructor with many parameters (some optional) is unreadable:
 *            new Pizza("large", true, false, true, false, 3)  <- what do those mean? and the
 *            "telescoping constructors" for every combination of optional fields.
 * SOLUTION : a separate Builder collects the values with named methods, then build() creates the
 *            finished, immutable object after checking it is valid.
 * TRADE-OFF: more code (a second class). For 2-3 required fields, or for records, a plain constructor
 *            or a static factory is simpler.
 */
public class _4_Builder {

    // ============================================
    // THE PRODUCT - immutable, with a private constructor
    // ============================================

    static final class Pizza {
        private final String size;                                 // required
        private final boolean extraCheese;                         // optional
        private final boolean thinCrust;                           // optional
        private final List<String> toppings;                       // optional, zero or more

        private Pizza(Builder b) {
            this.size = b.size;
            this.extraCheese = b.extraCheese;
            this.thinCrust = b.thinCrust;
            this.toppings = List.copyOf(b.toppings);               // defensive copy: the pizza is immutable
        }

        static Builder builder(String size) {                      // required values go in the entry point
            return new Builder(size);
        }

        @Override
        public String toString() {
            return size + " pizza" + (thinCrust ? ", thin crust" : "") + (extraCheese ? ", extra cheese" : "")
                    + (toppings.isEmpty() ? ", no toppings" : ", toppings " + toppings);
        }

        // ============================================
        // THE BUILDER - a nested static class; every setter returns 'this' so calls can be CHAINED
        // ============================================

        static final class Builder {
            private final String size;
            private boolean extraCheese;
            private boolean thinCrust;
            private final List<String> toppings = new ArrayList<>();

            private Builder(String size) {
                this.size = Objects.requireNonNull(size, "size is required");
            }

            Builder extraCheese() {
                this.extraCheese = true;
                return this;
            }

            Builder thinCrust() {
                this.thinCrust = true;
                return this;
            }

            Builder topping(String topping) {
                this.toppings.add(topping);
                return this;
            }

            Pizza build() {
                // validation of the WHOLE object happens in one place, before it exists
                if (!List.of("small", "medium", "large").contains(size)) {
                    throw new IllegalStateException("unknown size '" + size + "'");
                }
                if (toppings.size() > 5) {
                    throw new IllegalStateException("too many toppings: " + toppings.size() + " (max 5)");
                }
                return new Pizza(this);
            }
        }
    }

    // ============================================
    // THE PROBLEM THE BUILDER SOLVES, for comparison
    // ============================================

    static final class UnreadablePizza {
        UnreadablePizza(String size, boolean extraCheese, boolean thinCrust, boolean olives, boolean mushrooms) {
        }
    }

    public static void main(String[] args) {

        // what do these booleans mean? you must open the constructor to find out
        new UnreadablePizza("large", true, false, true, false);

        // the builder reads like a sentence
        Pizza margherita = Pizza.builder("medium").build();
        Pizza loaded = Pizza.builder("large")
                .thinCrust()
                .extraCheese()
                .topping("mushrooms")
                .topping("olives")
                .build();
        System.out.println(margherita);
        System.out.println(loaded);

        // a builder can be used step by step, in a loop, or conditionally
        Pizza.Builder custom = Pizza.builder("small");
        for (String t : List.of("ham", "pineapple")) {
            custom.topping(t);
        }
        if (true) {                                                // imagine a real condition here
            custom.thinCrust();
        }
        System.out.println(custom.build());

        // validation protects us
        try {
            Pizza.builder("gigantic").build();
        } catch (IllegalStateException e) {
            System.out.println("rejected: " + e.getMessage());
        }
        try {
            Pizza.Builder many = Pizza.builder("large");
            for (int i = 1; i <= 6; i++) many.topping("t" + i);
            many.build();
        } catch (IllegalStateException e) {
            System.out.println("rejected: " + e.getMessage());
        }
        try {
            Pizza.builder(null);
        } catch (NullPointerException e) {
            System.out.println("rejected: " + e.getMessage());
        }

        // the product is immutable, even though the builder was reused
        Pizza.Builder reusable = Pizza.builder("small").topping("ham");
        Pizza first = reusable.build();
        reusable.topping("egg");
        System.out.println("first pizza is unaffected by later builder changes: " + first);

        // ============================================
        // WHEN IT MAKES THE CODE WORSE (exit-test material)
        // - A class with 2 fields: `new Point(x, y)` is clearer than Point.builder().x(1).y(2).build().
        // - Java records already give you a constructor with named components; use a compact
        //   constructor for validation and add a builder only if there are MANY optional fields.
        // - Libraries like Lombok's @Builder can write this boilerplate for you in real projects.
        // ============================================
    }
}
