// Tags: #Java #ModernJava #ModernJavaCapstone | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;
import java.util.stream.Collectors;

/**
 * CAPSTONE: a small payment system that uses the modern features together.
 *  - sealed interface  : the set of payment methods is CLOSED
 *  - records           : immutable data with validation in compact constructors
 *  - pattern switch    : fees and descriptions, exhaustive with NO default
 *  - record patterns   : read a record's parts inside the switch
 *  - java.time         : card expiry
 *  - text block, var   : the report
 * Money uses BigDecimal (never double) because binary floating point cannot represent 0.10 exactly.
 */
public class _7_ModernJavaCapstone {

    // ---------- the closed family of payment methods ----------
    sealed interface PaymentMethod permits Card, BankTransfer, Wallet { }

    record Card(String last4, YearMonth expires) implements PaymentMethod {
        Card {
            Objects.requireNonNull(last4);
            Objects.requireNonNull(expires);
            if (!last4.matches("\\d{4}")) {
                throw new IllegalArgumentException("last4 must be 4 digits: " + last4);
            }
        }
    }

    record BankTransfer(String iban) implements PaymentMethod {
        BankTransfer {
            if (iban == null || iban.length() < 10) {
                throw new IllegalArgumentException("IBAN too short");
            }
        }
    }

    record Wallet(String provider, boolean verified) implements PaymentMethod { }

    // ---------- a payment request, and a closed set of outcomes ----------
    record Payment(String id, BigDecimal amount, PaymentMethod method) {
        Payment {
            Objects.requireNonNull(id);
            Objects.requireNonNull(method);
            if (amount == null || amount.signum() <= 0) {
                throw new IllegalArgumentException("amount must be positive: " + amount);
            }
            amount = amount.setScale(2, RoundingMode.HALF_UP);          // normalize to cents
        }
    }

    sealed interface Outcome permits Approved, Declined { }

    record Approved(Payment payment, BigDecimal fee) implements Outcome { }

    record Declined(Payment payment, String reason) implements Outcome { }

    // ---------- business rules ----------
    static BigDecimal fee(Payment p) {
        return switch (p.method()) {                                    // sealed: exhaustive, no default
            case Card c -> p.amount().multiply(new BigDecimal("0.029")).add(new BigDecimal("0.30"));
            case BankTransfer b -> new BigDecimal("0.50");
            case Wallet w -> p.amount().multiply(new BigDecimal("0.015"));
        };
    }

    static Outcome process(Payment p, LocalDate today) {
        return switch (p.method()) {
            case Card(String last4, YearMonth expires) when expires.isBefore(YearMonth.from(today)) ->
                    new Declined(p, "card ending " + last4 + " expired " + expires);
            case Wallet(String provider, boolean verified) when !verified ->
                    new Declined(p, provider + " wallet is not verified");
            case BankTransfer b when p.amount().compareTo(new BigDecimal("10000")) > 0 ->
                    new Declined(p, "bank transfers are limited to 10,000.00");
            case PaymentMethod m ->
                    new Approved(p, fee(p).setScale(2, RoundingMode.HALF_UP));
        };
    }

    static String describe(PaymentMethod m) {
        return switch (m) {
            case Card c -> "card ****" + c.last4();
            case BankTransfer b -> "bank transfer " + b.iban().substring(0, 4) + "...";
            case Wallet w -> w.provider() + " wallet";
        };
    }

    public static void main(String[] args) {

        var today = LocalDate.of(2026, 3, 1);                           // fixed so the output never changes

        var payments = List.of(
                new Payment("P1", new BigDecimal("100.00"), new Card("4242", YearMonth.of(2028, 5))),
                new Payment("P2", new BigDecimal("250.50"), new BankTransfer("DE89370400440532013000")),
                new Payment("P3", new BigDecimal("40"), new Wallet("PayPal", true)),
                new Payment("P4", new BigDecimal("75.00"), new Card("1111", YearMonth.of(2025, 12))),
                new Payment("P5", new BigDecimal("20.00"), new Wallet("QuickPay", false)),
                new Payment("P6", new BigDecimal("12000.00"), new BankTransfer("GB29NWBK60161331926819")));

        List<Outcome> outcomes = new ArrayList<>();
        for (var p : payments) {
            outcomes.add(process(p, today));
        }

        for (var outcome : outcomes) {
            String line = switch (outcome) {
                case Approved(Payment p, BigDecimal fee) ->
                        "APPROVED %s %8s via %-22s fee %s".formatted(p.id(), p.amount(), describe(p.method()), fee);
                case Declined(Payment p, String reason) ->
                        "DECLINED %s %8s via %-22s -> %s".formatted(p.id(), p.amount(), describe(p.method()), reason);
            };
            System.out.println(line);
        }

        // ---------- totals with streams over the sealed type ----------
        BigDecimal totalFees = outcomes.stream()
                .filter(o -> o instanceof Approved)
                .map(o -> ((Approved) o).fee())
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        Map<String, Long> countByKind = outcomes.stream()
                .collect(Collectors.groupingBy(o -> o.getClass().getSimpleName(), TreeMap::new, Collectors.counting()));
        System.out.println("outcomes: " + countByKind + ", total fees collected: " + totalFees);

        // ---------- a text-block report ----------
        long approved = countByKind.getOrDefault("Approved", 0L);
        String report = """
                === Daily report for %s ===
                payments processed : %d
                approved           : %d
                declined           : %d
                fees collected     : %s
                """.formatted(today, outcomes.size(), approved, outcomes.size() - approved, totalFees);
        System.out.print(report);

        // ---------- validation still protects us ----------
        try {
            new Payment("BAD", new BigDecimal("-5"), new Wallet("X", true));
        } catch (IllegalArgumentException e) {
            System.out.println("rejected at construction: " + e.getMessage());
        }
        try {
            new Card("12a4", YearMonth.of(2030, 1));
        } catch (IllegalArgumentException e) {
            System.out.println("rejected at construction: " + e.getMessage());
        }

        // ============================================
        // EXIT TEST NOTES (write your own version after retyping this file)
        // Where a modern feature replaced boilerplate:
        //   the records (Card, Wallet, Payment...) replace roughly 25 lines each of fields, constructors,
        //   getters, equals, hashCode, toString; the sealed + switch pair replaces an if/else chain AND adds
        //   compile-time exhaustiveness.
        // Where it would be showing off:
        //   the last case "case PaymentMethod m" in process() is a catch-all that only works because the
        //   earlier cases are guards; a plain if-chain on a method's own fields would be easier to read for
        //   a newcomer. Also var on every line would hurt more than help.
        // ============================================
    }
}
