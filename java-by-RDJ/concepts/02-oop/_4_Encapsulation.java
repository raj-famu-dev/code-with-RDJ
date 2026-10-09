public class _4_Encapsulation {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THE PROBLEM WITH PUBLIC FIELDS
        // In _1_ClassesAndObjects, fields were public - meaning ANY code,
        // anywhere, could set them to ANY value, even invalid ones.
        // ============================================

        BankAccountUnsafe unsafeAccount = new BankAccountUnsafe();
        unsafeAccount.balance = -5000;  // completely invalid, but Java allows it!
        System.out.println("Unsafe account balance: " + unsafeAccount.balance);
        // A bank account should NEVER be able to go negative like this from
        // outside code - this is exactly the problem encapsulation solves


        // ============================================
        // SECTION 2: WHAT IS ENCAPSULATION?
        // The practice of making fields PRIVATE (hidden from outside access)
        // and only allowing controlled access through public methods
        // (getters to read, setters to write) - often called "data hiding"
        // ============================================

        BankAccountSafe safeAccount = new BankAccountSafe("RDJ", 1000);

        // safeAccount.balance = -5000;  // COMPILE ERROR - balance is private now!
        // You literally CANNOT do this anymore - the compiler blocks it


        // ============================================
        // SECTION 3: GETTERS - CONTROLLED READ ACCESS
        // A public method that returns the value of a private field
        // ============================================

        System.out.println("Account holder: " + safeAccount.getOwnerName());
        System.out.println("Current balance: " + safeAccount.getBalance());


        // ============================================
        // SECTION 4: SETTERS - CONTROLLED WRITE ACCESS WITH VALIDATION
        // A public method that updates a private field, but can VALIDATE
        // the input first and reject bad values instead of blindly accepting them
        // ============================================

        safeAccount.setBalance(2000);  // valid, gets accepted
        System.out.println("Balance after valid setBalance: " + safeAccount.getBalance());

        safeAccount.setBalance(-500);  // invalid, should be rejected
        System.out.println("Balance after INVALID setBalance attempt: " + safeAccount.getBalance());
        // Notice: balance stays unchanged from before, because the setter rejected it


        // ============================================
        // SECTION 5: METHODS THAT SAFELY MODIFY STATE (BETTER THAN RAW SETTERS)
        // Instead of just a generic setter, real classes often expose
        // MEANINGFUL actions with their own built-in validation logic
        // ============================================

        safeAccount.deposit(500);
        System.out.println("Balance after deposit: " + safeAccount.getBalance());

        safeAccount.withdraw(300);
        System.out.println("Balance after withdraw: " + safeAccount.getBalance());

        safeAccount.withdraw(999999);  // trying to withdraw more than available
        System.out.println("Balance after INVALID withdraw attempt: " + safeAccount.getBalance());


        // ============================================
        // SECTION 6: READ-ONLY FIELDS (GETTER, BUT NO SETTER AT ALL)
        // Some fields should NEVER change after creation - simply don't
        // write a setter for them, and they become effectively read-only
        // from outside the class
        // ============================================

        System.out.println("Account number (read-only): " + safeAccount.getAccountNumber());
        // There's no setAccountNumber() method at all - by design


        // ============================================
        // SECTION 7: WHY THIS MATTERS - REAL-WORLD REASONING
        // ============================================

        // 1. VALIDATION: setters can reject bad data before it corrupts your object's state
        // 2. FLEXIBILITY: you can change HOW a field is stored internally later,
        //    without breaking any code that uses the getter/setter (they're insulated
        //    from the internal implementation details)
        // 3. CONTROL: you decide exactly what external code CAN and CANNOT do to your object
        // 4. DEBUGGING: since only your class's own methods can modify private fields,
        //    if something goes wrong, you know EXACTLY where to look
    }
}


// ============================================
// UNSAFE VERSION - NO ENCAPSULATION (fields are public, directly exposed)
// ============================================

class BankAccountUnsafe {
    public double balance;  // anyone, anywhere, can set this to anything
}


// ============================================
// SAFE VERSION - PROPER ENCAPSULATION
// ============================================

class BankAccountSafe {

    // --- PRIVATE FIELDS: hidden from outside access ---
    private String ownerName;
    private double balance;
    private final String accountNumber;  // 'final' = set once, never changes after

    // Constructor
    BankAccountSafe(String ownerName, double initialBalance) {
        this.ownerName = ownerName;
        this.balance = (initialBalance >= 0) ? initialBalance : 0;
        this.accountNumber = generateAccountNumber();
    }

    // --- GETTERS: controlled read access ---
    String getOwnerName() {
        return ownerName;
    }

    double getBalance() {
        return balance;
    }

    String getAccountNumber() {
        return accountNumber;
    }

    // --- SETTER WITH VALIDATION ---
    void setBalance(double newBalance) {
        if (newBalance >= 0) {
            this.balance = newBalance;
        } else {
            System.out.println("Rejected: balance cannot be negative.");
        }
    }

    // --- MEANINGFUL ACTION METHODS (better design than raw setters alone) ---
    void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
        } else {
            System.out.println("Rejected: deposit amount must be positive.");
        }
    }

    void withdraw(double amount) {
        if (amount <= 0) {
            System.out.println("Rejected: withdrawal amount must be positive.");
        } else if (amount > balance) {
            System.out.println("Rejected: insufficient funds.");
        } else {
            balance -= amount;
        }
    }

    // Private helper method - not exposed outside the class at all
    private String generateAccountNumber() {
        return "ACC-" + (int) (Math.random() * 100000);
    }
}