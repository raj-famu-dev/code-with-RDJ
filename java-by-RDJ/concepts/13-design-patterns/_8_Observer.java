// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.function.Consumer;

/**
 * OBSERVER: let objects subscribe to events from another object, without the source knowing who they are.
 * PROBLEM  : when something changes (an order is placed, a price moves) several other parts must react
 *            (send an email, update stats, write an audit log). If the source calls them all directly it is
 *            welded to every one of them, and adding a reaction means editing the source.
 * SOLUTION : the source (the "subject" or "publisher") keeps a list of listeners behind one small interface
 *            and notifies them. Listeners register and unregister themselves.
 * TRADE-OFF: control flow becomes indirect (hard to trace "who runs when I fire this?"); the order of
 *            listeners may matter; a listener that throws or is slow can break everyone; and forgetting to
 *            unregister leaks memory (the publisher keeps listeners alive).
 */
public class _8_Observer {

    record OrderPlaced(String orderId, double total) { }

    interface OrderListener {
        void onOrderPlaced(OrderPlaced event);
    }

    // ============================================
    // THE SUBJECT / PUBLISHER
    // ============================================

    static class OrderService {
        // CopyOnWriteArrayList: safe to iterate even if a listener unsubscribes while being notified
        private final List<OrderListener> listeners = new CopyOnWriteArrayList<>();

        void subscribe(OrderListener listener) {
            listeners.add(listener);
        }

        void unsubscribe(OrderListener listener) {
            listeners.remove(listener);
        }

        void placeOrder(String id, double total) {
            OrderPlaced event = new OrderPlaced(id, total);
            for (OrderListener listener : listeners) {
                try {
                    listener.onOrderPlaced(event);
                } catch (RuntimeException e) {                     // one bad listener must not stop the others
                    System.out.println("  (listener failed: " + e.getMessage() + ", continuing)");
                }
            }
        }
    }

    // ============================================
    // THE OBSERVERS - each knows nothing about the others
    // ============================================

    static class EmailReceipt implements OrderListener {
        public void onOrderPlaced(OrderPlaced e) {
            System.out.println("  email: receipt for " + e.orderId() + " total " + e.total());
        }
    }

    static class SalesStats implements OrderListener {
        double revenue;
        int orders;

        public void onOrderPlaced(OrderPlaced e) {
            revenue += e.total();
            orders++;
        }
    }

    static class FraudCheck implements OrderListener {
        public void onOrderPlaced(OrderPlaced e) {
            if (e.total() > 1000) {
                throw new IllegalStateException("order " + e.orderId() + " flagged as suspicious");
            }
        }
    }

    public static void main(String[] args) {

        OrderService service = new OrderService();
        EmailReceipt email = new EmailReceipt();
        SalesStats stats = new SalesStats();

        System.out.println("--- no listeners ---");
        service.placeOrder("A-1", 20.0);                           // nothing happens, and the service is fine with that

        System.out.println("--- three listeners ---");
        service.subscribe(email);
        service.subscribe(new FraudCheck());                       // this one throws for big orders
        service.subscribe(stats);
        service.placeOrder("A-2", 50.0);
        service.placeOrder("A-3", 2500.0);                         // FraudCheck fails but email and stats still run

        System.out.println("--- lambdas as listeners (it is a functional interface) ---");
        List<String> audit = new ArrayList<>();
        OrderListener auditor = e -> audit.add(e.orderId());
        service.subscribe(auditor);
        service.placeOrder("A-4", 10.0);
        System.out.println("  audit log: " + audit);

        System.out.println("--- unsubscribing ---");
        service.unsubscribe(email);
        service.placeOrder("A-5", 5.0);
        System.out.println("  (no email line above: the listener was removed)");

        System.out.printf("stats: %d orders, revenue %.2f%n", stats.orders, stats.revenue);

        // ============================================
        // THE SAME IDEA, SMALLER: a generic event bus with Consumer<T>
        // ============================================

        class Topic<T> {
            private final List<Consumer<T>> subscribers = new ArrayList<>();

            void subscribe(Consumer<T> subscriber) {
                subscribers.add(subscriber);
            }

            void publish(T value) {
                subscribers.forEach(s -> s.accept(value));
            }
        }
        Topic<String> news = new Topic<>();
        news.subscribe(s -> System.out.println("  reader 1 got: " + s));
        news.subscribe(s -> System.out.println("  reader 2 got: " + s.toUpperCase()));
        news.publish("Java 21 released");

        // JDK/Java ecosystem examples: GUI button listeners (Swing/JavaFX), java.beans.PropertyChangeListener,
        // Spring's ApplicationEventPublisher, and reactive streams (Flow.Publisher/Subscriber).
        // (java.util.Observable was deprecated in Java 9: do not use it.)

        // ============================================
        // WHEN IT MAKES THE CODE WORSE (exit-test material)
        // - Only ONE thing ever reacts: call it directly. The indirection hides a simple call.
        // - Listeners that must run in a strict order or share a transaction: the pattern gives you no order or
        //   atomicity, and failures become silent (note how we had to catch exceptions to protect the rest).
        // - Long-lived publishers with short-lived listeners and no unsubscribe: a memory leak.
        // ============================================
    }
}
