// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.List;

/**
 * CAPSTONE: refactor a small bank from "everything in one class" to Strategy + Observer, with a BEFORE and AFTER
 * that can be compared line by line.
 *
 * NOTE: projects/project-03-bank-system is only a SPECIFICATION so far. This file is a miniature bank with the
 * same ideas (account types, fees, history). When you build project-03 yourself, do this same refactor on YOUR code.
 *
 * Money is whole CENTS in a long (never double).
 *
 * WHAT HURT BEFORE:
 *   1. Fee rules are an if/else on account type inside the account: a new account type means editing it.
 *   2. The account itself prints receipts and "emails" the manager: it knows about notifications.
 * PATTERNS APPLIED:
 *   1. STRATEGY  for the monthly fee   (_7_Strategy)
 *   2. OBSERVER  for reacting to transactions (_8_Observer)
 * (SOLID connection: S - one job per class; O - add behaviour without editing; D - depend on interfaces.)
 */
public class _10_RefactorBankSystem {

    static String dollars(long cents) {
        return String.format("%d.%02d", cents / 100, Math.abs(cents % 100));
    }

    // =========================================================================================
    // BEFORE
    // =========================================================================================

    static class BadAccount {
        final String type;                                         // "checking", "savings", "premium"
        long balanceCents;

        BadAccount(String type, long balanceCents) {
            this.type = type;
            this.balanceCents = balanceCents;
        }

        void withdraw(long cents) {
            if (cents > balanceCents) {
                throw new IllegalStateException("insufficient funds");
            }
            balanceCents -= cents;
            System.out.println("  [bad] receipt printed: withdrew " + dollars(cents));       // presentation inside the account
            if (cents >= 100_000) {
                System.out.println("  [bad] emailing manager: large withdrawal");            // notification inside the account
            }
        }

        long monthlyFee() {
            if (type.equals("checking")) return balanceCents < 50_000 ? 1_200 : 0;           // fee rules inside the account
            if (type.equals("savings")) return 0;
            if (type.equals("premium")) return 2_500;
            throw new IllegalArgumentException("unknown type " + type);                      // a new type = edit this method
        }
    }

    // =========================================================================================
    // AFTER - pattern 1: STRATEGY for fees
    // =========================================================================================

    @FunctionalInterface
    interface FeePolicy {
        long monthlyFee(long balanceCents);
    }

    static final FeePolicy CHECKING_FEE = balance -> balance < 50_000 ? 1_200 : 0;
    static final FeePolicy NO_FEE = balance -> 0;
    static final FeePolicy PREMIUM_FEE = balance -> 2_500;

    // =========================================================================================
    // AFTER - pattern 2: OBSERVER for reactions
    // =========================================================================================

    record TransactionEvent(String accountId, String kind, long cents, long balanceAfterCents) { }

    interface TransactionListener {
        void onTransaction(TransactionEvent event);
    }

    static class InsufficientFundsException extends Exception {
        private static final long serialVersionUID = 1L;
        final long shortfallCents;

        InsufficientFundsException(long shortfallCents) {
            super("short by " + dollars(shortfallCents));
            this.shortfallCents = shortfallCents;
        }
    }

    // The account now has ONE job: keep a correct balance. It does not print, email or know fee rules.
    static class Account {
        private final String id;
        private long balanceCents;
        private final FeePolicy feePolicy;                         // injected strategy
        private final List<TransactionListener> listeners = new ArrayList<>();   // observers

        Account(String id, long openingCents, FeePolicy feePolicy) {
            this.id = id;
            this.balanceCents = openingCents;
            this.feePolicy = feePolicy;
        }

        void addListener(TransactionListener l) {
            listeners.add(l);
        }

        void withdraw(long cents) throws InsufficientFundsException {
            if (cents > balanceCents) {
                throw new InsufficientFundsException(cents - balanceCents);
            }
            balanceCents -= cents;
            publish("WITHDRAW", cents);
        }

        void deposit(long cents) {
            balanceCents += cents;
            publish("DEPOSIT", cents);
        }

        void applyMonthlyFee() {
            long fee = feePolicy.monthlyFee(balanceCents);         // delegate the rule
            if (fee > 0) {
                balanceCents -= fee;
                publish("FEE", fee);
            }
        }

        long balanceCents() {
            return balanceCents;
        }

        String id() {
            return id;
        }

        private void publish(String kind, long cents) {
            TransactionEvent event = new TransactionEvent(id, kind, cents, balanceCents);
            for (TransactionListener l : listeners) {
                l.onTransaction(event);
            }
        }
    }

    // Each reaction is its own class, added WITHOUT touching Account
    static class ReceiptPrinter implements TransactionListener {
        public void onTransaction(TransactionEvent e) {
            System.out.println("  receipt: " + e.kind() + " " + dollars(e.cents()) + " on " + e.accountId()
                    + ", balance " + dollars(e.balanceAfterCents()));
        }
    }

    static class LargeWithdrawalAlert implements TransactionListener {
        final List<String> alerts = new ArrayList<>();

        public void onTransaction(TransactionEvent e) {
            if (e.kind().equals("WITHDRAW") && e.cents() >= 100_000) {
                alerts.add("large withdrawal of " + dollars(e.cents()) + " on " + e.accountId());
            }
        }
    }

    static class StatementHistory implements TransactionListener {
        final List<TransactionEvent> history = new ArrayList<>();

        public void onTransaction(TransactionEvent e) {
            history.add(e);
        }
    }

    public static void main(String[] args) throws Exception {

        System.out.println("=== BEFORE ===");
        BadAccount bad = new BadAccount("checking", 250_000);
        bad.withdraw(120_000);
        System.out.println("  fee for this type: " + dollars(bad.monthlyFee()));
        try {
            new BadAccount("student", 100).monthlyFee();           // needs an edit to the class to support a new kind
        } catch (IllegalArgumentException e) {
            System.out.println("  new account type unsupported until the class is edited: " + e.getMessage());
        }

        System.out.println("=== AFTER ===");
        Account checking = new Account("CHK-1", 250_000, CHECKING_FEE);
        Account premium = new Account("PRM-1", 900_000, PREMIUM_FEE);
        Account student = new Account("STU-1", 40_000, balance -> 300);   // a NEW kind: one lambda, no class edited

        ReceiptPrinter printer = new ReceiptPrinter();
        LargeWithdrawalAlert alert = new LargeWithdrawalAlert();
        StatementHistory history = new StatementHistory();
        for (Account a : List.of(checking, premium, student)) {
            a.addListener(printer);
            a.addListener(alert);
            a.addListener(history);
        }

        checking.withdraw(120_000);
        premium.deposit(50_000);
        try {
            student.withdraw(90_000);
        } catch (InsufficientFundsException e) {
            System.out.println("  rejected: " + e.getMessage() + " (shortfall cents = " + e.shortfallCents + ")");
        }

        System.out.println("--- month end ---");
        for (Account a : List.of(checking, premium, student)) {
            a.applyMonthlyFee();
        }

        System.out.println("--- results ---");
        for (Account a : List.of(checking, premium, student)) {
            System.out.println("  " + a.id() + " balance " + dollars(a.balanceCents()));
        }
        System.out.println("  alerts: " + alert.alerts);
        System.out.println("  history entries recorded: " + history.history.size());

        System.out.println("--- does the Strategy give the same fees as the old if/else? ---");
        boolean allEqual = true;
        for (long balance : new long[]{0, 49_999, 50_000, 130_000}) {
            long oldFee = new BadAccount("checking", balance).monthlyFee();
            long newFee = CHECKING_FEE.monthlyFee(balance);
            allEqual &= oldFee == newFee;
        }
        System.out.println("  checking fee identical for 4 test balances: " + allEqual);
        System.out.println("  premium fee identical: " + (new BadAccount("premium", 1).monthlyFee() == PREMIUM_FEE.monthlyFee(1)));

        // ============================================
        // BEFORE / AFTER, HONESTLY
        // + Adding the student account needed ONE lambda, no edits to Account.
        // + Adding a reaction (the alert, the history) needed one new class, no edits to Account.
        // + Account is small enough to test alone: no printing, no email.
        // - The code is longer and has more types than the BEFORE version.
        // - A new reader has to discover which listeners and policy an Account was given.
        // For two account types and one print line, the BEFORE version would have been fine. These patterns pay
        // for themselves when the number of fee rules and reactions keeps growing.
        // ============================================
    }
}
