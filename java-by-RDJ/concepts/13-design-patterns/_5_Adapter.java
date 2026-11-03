// Tags: #Java #DesignPatterns #SOLID #Adapter | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.List;

/**
 * ADAPTER: make a class with the WRONG interface fit the interface your code expects.
 * PROBLEM  : you own code written against interface A, and a library or legacy class (which you
 *            cannot or should not edit) offers the same capability through a different interface B.
 * SOLUTION : write a small class that IMPLEMENTS A and internally CALLS B (like a travel plug adapter).
 * TRADE-OFF: one more layer, and it can hide a poor fit (units, error handling, performance).
 *            If you CAN change the original class, change it instead.
 */
public class _5_Adapter {

    // ============================================
    // THE INTERFACE OUR APPLICATION EXPECTS ("target")
    // ============================================

    interface PaymentGateway {
        boolean charge(String customerId, double dollars);
    }

    // Our own implementation - already fits
    static class InHousePayments implements PaymentGateway {
        public boolean charge(String customerId, double dollars) {
            System.out.println("  in-house: charged " + customerId + " $" + String.format("%.2f", dollars));
            return true;
        }
    }

    // ============================================
    // THE THIRD-PARTY / LEGACY CLASS ("adaptee") - we cannot edit it, and its interface is different:
    // amounts in CENTS (long), a numeric account id, and a status CODE instead of a boolean.
    // ============================================

    static class LegacyBillingSystem {
        int makePayment(long accountNumber, long amountInCents) {
            System.out.println("  legacy: account " + accountNumber + " debited " + amountInCents + " cents");
            return amountInCents > 100_000 ? 2 : 0;                // 0 = OK, 2 = LIMIT_EXCEEDED
        }
    }

    // ============================================
    // THE ADAPTER - speaks OUR interface, calls THEIR methods, translates units and results
    // ============================================

    static class LegacyBillingAdapter implements PaymentGateway {
        private final LegacyBillingSystem legacy;                  // composition: the adapter HAS a legacy system

        LegacyBillingAdapter(LegacyBillingSystem legacy) {
            this.legacy = legacy;
        }

        @Override
        public boolean charge(String customerId, double dollars) {
            long account = Long.parseLong(customerId.replace("C-", ""));   // "C-1042" -> 1042
            long cents = Math.round(dollars * 100);                // dollars -> cents (rounded, not truncated)
            int code = legacy.makePayment(account, cents);
            return code == 0;                                      // code -> boolean
        }
    }

    // ============================================
    // OUR CODE: depends ONLY on PaymentGateway and has no idea which one it got
    // ============================================

    static class CheckoutService {
        private final PaymentGateway gateway;

        CheckoutService(PaymentGateway gateway) {
            this.gateway = gateway;
        }

        String checkout(String customerId, double total) {
            return gateway.charge(customerId, total) ? "paid" : "payment failed";
        }
    }

    public static void main(String[] args) {

        CheckoutService inHouse = new CheckoutService(new InHousePayments());
        System.out.println("in-house result: " + inHouse.checkout("C-7", 19.99));

        // the legacy system plugs in through the adapter; CheckoutService is not touched
        CheckoutService legacy = new CheckoutService(new LegacyBillingAdapter(new LegacyBillingSystem()));
        System.out.println("legacy result:   " + legacy.checkout("C-1042", 19.99));
        System.out.println("legacy over its limit: " + legacy.checkout("C-1042", 1500.00));

        // the classic rounding trap the adapter must handle: binary doubles are not exact, so 19.99 * 100 is 1998.9999999999998
        System.out.println("19.99 dollars -> " + Math.round(19.99 * 100) + " cents (truncating would give " + (long) (19.99 * 100) + ")");

        // JDK examples of adapters you already use:
        //   Arrays.asList(array)  : adapts an array to the List interface
        //   InputStreamReader     : adapts a byte stream (InputStream) to a character stream (Reader)
        List<String> adapted = java.util.Arrays.asList("a", "b");
        System.out.println("Arrays.asList adapts an array to a List: " + adapted);

        // ============================================
        // WHEN IT MAKES THE CODE WORSE (exit-test material)
        // - Adapting a class YOU own and could simply fix: you are paying for a layer you do not need.
        // - A "thin" adapter that hides a real mismatch (e.g. silently dropping error details when the
        //   legacy code gives 5 different failure codes but the adapter reduces them to false).
        // - Stacking adapters on adapters: the real behaviour becomes impossible to trace.
        // ============================================
    }
}
