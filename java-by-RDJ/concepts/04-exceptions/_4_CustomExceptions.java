// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
public class _4_CustomExceptions {

    // A shared parent for every banking problem, so callers can catch them all at once
    static class BankException extends Exception {
        BankException(String message) {
            super(message);
        }
    }

    // CHECKED: the caller can reasonably recover (ask for a smaller amount)
    static class InsufficientFundsException extends BankException {
        private final double shortfall;           // extra data about WHAT went wrong

        InsufficientFundsException(double shortfall) {
            super("Insufficient funds, short by " + shortfall);
            this.shortfall = shortfall;
        }

        double getShortfall() {
            return shortfall;
        }
    }

    static class AccountLockedException extends BankException {
        AccountLockedException(String accountId) {
            super("Account " + accountId + " is locked");
        }
    }

    // UNCHECKED: passing a negative amount is a programming mistake, not a runtime condition
    static class InvalidAmountException extends RuntimeException {
        InvalidAmountException(double amount) {
            super("Amount must be positive but was " + amount);
        }
    }

    static class Account {
        private final String id;
        private double balance;
        private boolean locked;

        Account(String id, double balance, boolean locked) {
            this.id = id;
            this.balance = balance;
            this.locked = locked;
        }

        void withdraw(double amount) throws BankException {
            if (amount <= 0) throw new InvalidAmountException(amount);
            if (locked) throw new AccountLockedException(id);
            if (amount > balance) throw new InsufficientFundsException(amount - balance);
            balance -= amount;
        }

        double getBalance() {
            return balance;
        }
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHY MAKE YOUR OWN EXCEPTION
        // 'IllegalArgumentException' says "something was wrong".
        // 'InsufficientFundsException' says exactly WHAT was wrong, and can
        // carry data (the shortfall) so the caller can react.
        // ============================================

        Account account = new Account("ACC-1", 100.0, false);
        try {
            account.withdraw(150.0);
        } catch (InsufficientFundsException e) {
            System.out.println("Caught: " + e.getMessage() + " (shortfall field = " + e.getShortfall() + ")");
        } catch (BankException e) {
            System.out.println("Some other bank problem: " + e.getMessage());
        }


        // ============================================
        // SECTION 2: A HIERARCHY LETS CALLERS CHOOSE THEIR PRECISION
        // Catch the specific type to handle it specially, or the parent to
        // handle "any bank problem" the same way.
        // ============================================

        Account locked = new Account("ACC-2", 500.0, true);
        try {
            locked.withdraw(10.0);
        } catch (BankException e) {
            System.out.println("Caught via parent type: " + e.getMessage()
                    + " [" + e.getClass().getSimpleName() + "]");
        }


        // ============================================
        // SECTION 3: CHECKED OR UNCHECKED? THE DECISION
        // Extend Exception          -> caller MUST handle or declare it.
        //                              Use when a reasonable caller can recover.
        // Extend RuntimeException   -> caller is not forced.
        //                              Use for programming errors / invalid use.
        // Here: insufficient funds and locked accounts are normal business
        // outcomes (checked); a negative amount is a bug (unchecked).
        // ============================================

        try {
            account.withdraw(-20.0);
        } catch (InvalidAmountException e) {
            System.out.println("Caught unchecked: " + e.getMessage());
        } catch (BankException e) {
            System.out.println("Not reached for a negative amount");
        }


        // ============================================
        // SECTION 4: A SUCCESSFUL CALL, FOR CONTRAST
        // ============================================

        try {
            account.withdraw(30.0);
            System.out.println("Withdrew 30, balance now " + account.getBalance());
        } catch (BankException e) {
            System.out.println("Unexpected: " + e.getMessage());
        }


        // ============================================
        // SECTION 5: NAMING AND DESIGN TIPS
        // - End the name with "Exception".
        // - Give the constructor a message (and a cause, see _6).
        // - Add fields only for data a handler will actually use.
        // - Do not create a new exception type for every single error; make one
        //   only when a caller would handle it differently.
        // ============================================
    }
}
