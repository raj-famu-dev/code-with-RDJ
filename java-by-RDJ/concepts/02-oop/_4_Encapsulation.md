# `_4_Encapsulation.java`

## Concept
Encapsulation — hiding internal fields behind `private` access and exposing controlled read/write through public methods. The first of the four OOP pillars.

## Full Line-by-Line Breakdown

### `public class _4_Encapsulation {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: The Problem With Public Fields

**`BankAccountUnsafe unsafeAccount = new BankAccountUnsafe();`**
Creates an object of the "unsafe" version of a bank account, defined below.

**`unsafeAccount.balance = -5000;`**
Directly sets the `balance` field to a negative number — completely nonsensical for a real bank account, but Java allows it without complaint, since `balance` in this class is declared `public` with no protection at all.

**`System.out.println("Unsafe account balance: " + unsafeAccount.balance);`**
Confirms the invalid value was accepted — prints `-5000`, proving the problem this entire topic exists to solve.

---

### SECTION 2: What Is Encapsulation?

**`BankAccountSafe safeAccount = new BankAccountSafe("RDJ", 1000);`**
Creates an object of the "safe" version instead, using its constructor to set an owner name and initial balance properly.

**The commented-out line `// safeAccount.balance = -5000;`**
Left in deliberately to show what would happen if uncommented: a **compile error**. Since `balance` is `private` in `BankAccountSafe`, external code (like `main()`) has no direct access to it at all — the compiler itself blocks the attempt, rather than just discouraging it by convention.

---

### SECTION 3: Getters — Controlled Read Access

**`safeAccount.getOwnerName()`**
Calls a public method that simply returns the private `ownerName` field's current value — this is the only way outside code can read it.

**`safeAccount.getBalance()`**
Same pattern, returning the private `balance` field.

---

### SECTION 4: Setters — Controlled Write Access With Validation

**`safeAccount.setBalance(2000);`**
Calls the setter with a valid, non-negative value — it passes validation and updates `balance` to `2000`.

**`safeAccount.setBalance(-500);`**
Calls the setter with an invalid negative value. Since the setter checks `if (newBalance >= 0)` before assigning, this call is **rejected** — the balance stays at whatever it was before (`2000`), and a rejection message prints instead.

**The two `println` lines**
Confirm the contrast directly: the valid call changed the balance, the invalid call didn't — proving the setter's validation logic actually works, not just exists cosmetically.

---

### SECTION 5: Methods That Safely Modify State

**`safeAccount.deposit(500);`**
Calls a purpose-built method (not a generic setter) that adds to the balance, but only if the amount is positive.

**`safeAccount.withdraw(300);`**
Calls a similar purpose-built method that subtracts from the balance, but only if the amount is positive **and** doesn't exceed the current balance.

**`safeAccount.withdraw(999999);`**
Attempts to withdraw far more than the account holds. The method's validation (`amount > balance`) catches this and **rejects** it, printing an "insufficient funds" message — the balance remains unchanged.

**Why this is "better than raw setters":** `deposit()` and `withdraw()` aren't just "set this field to any value" — they represent meaningful, real-world actions, each with validation logic specific to what that action should and shouldn't allow.

---

### SECTION 6: Read-Only Fields

**`safeAccount.getAccountNumber()`**
Calls a getter for `accountNumber` — but notice there is **no corresponding setter** anywhere in the class. This isn't an oversight; it's intentional. Since an account number should never change after the account is created, simply never writing a setter makes the field permanently read-only from outside the class, with zero extra effort required.

---

### SECTION 7: Why This Matters
No new code here — just the real-world reasoning summarized in four points: validation (rejecting bad data), flexibility (changing internal storage without breaking external code), control (deciding exactly what's allowed), and debugging (knowing exactly where state changes can originate from, since only the class's own methods can touch its private fields).

---

### The `BankAccountUnsafe` Class

```java
class BankAccountUnsafe {
    public double balance;
}
```
A single `public` field with zero protection — anyone, anywhere, can set it to literally any value, including nonsensical ones. This exists purely as a contrast to demonstrate the problem encapsulation solves.

---

### The `BankAccountSafe` Class

**Fields:**
```java
private String ownerName;
private double balance;
private final String accountNumber;
```
All three fields are `private` — completely hidden from direct outside access. `accountNumber` is additionally `final`, meaning once set in the constructor, it can never be reassigned again, even from within the class itself.

**Constructor:**
```java
BankAccountSafe(String ownerName, double initialBalance) {
    this.ownerName = ownerName;
    this.balance = (initialBalance >= 0) ? initialBalance : 0;
    this.accountNumber = generateAccountNumber();
}
```
Uses a **ternary operator** (recap from `_3_Operators.java`) to validate the initial balance right at creation time: if a negative value is somehow passed in, it silently defaults to `0` instead. `accountNumber` is generated internally via a private helper method — the caller never supplies this directly at all.

**Getters:**
```java
String getOwnerName() { return ownerName; }
double getBalance() { return balance; }
String getAccountNumber() { return accountNumber; }
```
Each simply returns its corresponding private field's current value — straightforward, controlled read access.

**Setter with validation:**
```java
void setBalance(double newBalance) {
    if (newBalance >= 0) {
        this.balance = newBalance;
    } else {
        System.out.println("Rejected: balance cannot be negative.");
    }
}
```
The `if` check is the entire point of encapsulation in action — this is what actually protects the object's state, not just the fact that `balance` is private.

**`deposit()`:**
```java
void deposit(double amount) {
    if (amount > 0) {
        balance += amount;
    } else {
        System.out.println("Rejected: deposit amount must be positive.");
    }
}
```
Only accepts genuinely positive deposit amounts.

**`withdraw()`:**
```java
void withdraw(double amount) {
    if (amount <= 0) {
        System.out.println("Rejected: withdrawal amount must be positive.");
    } else if (amount > balance) {
        System.out.println("Rejected: insufficient funds.");
    } else {
        balance -= amount;
    }
}
```
Two separate rejection conditions checked in order: first that the amount itself is positive, then that it doesn't exceed the available balance. Only if both checks pass does the actual withdrawal happen.

**Private helper method:**
```java
private String generateAccountNumber() {
    return "ACC-" + (int) (Math.random() * 100000);
}
```
Marked `private` — this method isn't meant to be called from outside the class at all, only used internally by the constructor. `Math.random()` returns a decimal between `0.0` and `1.0`; multiplying by `100000` and casting to `int` produces a pseudo-random whole number used to build a unique-looking account number string.

## Key Rules / Gotchas Recap

- A setter with **no validation logic** barely improves on a public field — the real value of encapsulation is in what the setter *rejects*, not merely that it exists
- Not every field needs a setter — omitting one entirely (like `accountNumber`) makes a field effectively read-only after construction, with no extra code required
- `final` fields are a stronger guarantee than "no setter" — they're locked at the language level, not just by convention
- Purpose-built methods (`deposit()`/`withdraw()`) that represent meaningful actions are generally a better design than one generic `setBalance()` alone, since each can carry its own specific validation rules

## Why This Structure Exists

Public fields (as used in `_1_ClassesAndObjects.java`) allow any external code to set invalid state with zero resistance — as directly demonstrated in Section 1. Encapsulation is the first OOP pillar and the foundation for building objects that protect their own integrity, ensuring an object can never be pushed into a nonsensical state by code outside its own class.