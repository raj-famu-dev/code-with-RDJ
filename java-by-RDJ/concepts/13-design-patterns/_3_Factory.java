// Tags: #Java #DesignPatterns #SOLID #Factory | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

/**
 * FACTORY: move the decision "which concrete class do I create?" out of the caller.
 * PROBLEM  : code scattered with `new CreditCard(...)` / `new PayPal(...)` and if/else on a type string
 *            is welded to every concrete class; adding one means editing every place.
 * SOLUTION : callers ask a factory for "a Notifier of kind X" and get back the interface type.
 * TRADE-OFF: one more class/indirection. Worth it only when creation logic is non-trivial or likely to
 *            grow. For a single obvious class, plain `new` is simpler.
 */
public class _3_Factory {

    interface Notifier {
        String send(String message);
    }

    static class EmailNotifier implements Notifier {
        public String send(String message) {
            return "EMAIL -> " + message;
        }
    }

    static class SmsNotifier implements Notifier {
        public String send(String message) {
            return "SMS -> " + message.substring(0, Math.min(message.length(), 20));   // SMS truncates
        }
    }

    static class PushNotifier implements Notifier {
        private final String deviceToken;

        PushNotifier(String deviceToken) {
            this.deviceToken = deviceToken;
        }

        public String send(String message) {
            return "PUSH[" + deviceToken + "] -> " + message;
        }
    }

    // ============================================
    // STEP 1: THE PROBLEM - creation logic leaks into callers
    // ============================================

    static String callerWithoutFactory(String kind, String message) {
        Notifier n;
        if (kind.equals("email")) n = new EmailNotifier();
        else if (kind.equals("sms")) n = new SmsNotifier();
        else throw new IllegalArgumentException("unknown kind " + kind);
        return n.send(message);                                    // and this if/else is copy-pasted wherever notifiers are needed
    }

    // ============================================
    // STEP 2: SIMPLE (STATIC) FACTORY - the decision lives in ONE place
    // ============================================

    static class NotifierFactory {
        static Notifier create(String kind) {
            return switch (kind) {
                case "email" -> new EmailNotifier();
                case "sms" -> new SmsNotifier();
                case "push" -> new PushNotifier("device-42");
                default -> throw new IllegalArgumentException("unknown kind '" + kind + "'");
            };
        }
    }

    // ============================================
    // STEP 3: FACTORY METHOD - let SUBCLASSES decide what to create
    // The base class holds the shared workflow; the subclass picks the product.
    // ============================================

    static abstract class Alert {
        abstract Notifier createNotifier();                        // the FACTORY METHOD

        String raise(String text) {                                // shared workflow that never changes
            Notifier n = createNotifier();
            return "[ALERT] " + n.send(text);
        }
    }

    static class UrgentAlert extends Alert {
        Notifier createNotifier() {
            return new SmsNotifier();
        }
    }

    static class DailyDigestAlert extends Alert {
        Notifier createNotifier() {
            return new EmailNotifier();
        }
    }

    // ============================================
    // STEP 4: A REGISTRY OF SUPPLIERS - add new products WITHOUT editing the factory
    // (the Open/Closed principle from _1). Modern Java style.
    // ============================================

    static class RegistryFactory {
        private final Map<String, Supplier<Notifier>> creators;

        RegistryFactory(Map<String, Supplier<Notifier>> creators) {
            this.creators = Map.copyOf(creators);
        }

        Notifier create(String kind) {
            Supplier<Notifier> creator = creators.get(kind);
            if (creator == null) {
                throw new IllegalArgumentException("unknown kind '" + kind + "'; known: " + creators.keySet().stream().sorted().toList());
            }
            return creator.get();
        }
    }

    public static void main(String[] args) {

        System.out.println("--- without a factory ---");
        System.out.println(callerWithoutFactory("email", "server restarted"));

        System.out.println("--- simple factory ---");
        for (String kind : List.of("email", "sms", "push")) {
            Notifier n = NotifierFactory.create(kind);             // the caller only knows the INTERFACE
            System.out.println(n.send("Deployment finished successfully"));
        }
        try {
            NotifierFactory.create("pigeon");
        } catch (IllegalArgumentException e) {
            System.out.println("unknown kind: " + e.getMessage());
        }

        System.out.println("--- factory method ---");
        Alert urgent = new UrgentAlert();
        Alert digest = new DailyDigestAlert();
        System.out.println(urgent.raise("Database is down and customers are affected"));
        System.out.println(digest.raise("3 new signups today"));

        System.out.println("--- registry factory ---");
        RegistryFactory registry = new RegistryFactory(Map.of(
                "email", EmailNotifier::new,
                "sms", SmsNotifier::new,
                "slack", () -> message -> "SLACK -> " + message));   // a NEW kind added with one line, no factory edits
        System.out.println(registry.create("slack").send("hello team"));
        try {
            registry.create("fax");
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }

        // ============================================
        // WHEN IT MAKES THE CODE WORSE (exit-test material)
        // A "UserFactory" whose only method is `return new User(name)`. There is one product, one way to
        // build it and no decision to hide: the factory is pure ceremony. Also be careful with
        // "AbstractFactoryFactory" style layering: if the reader needs three jumps to find a `new`, stop.
        // ============================================
    }
}
