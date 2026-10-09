public class _3_Operators {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: ARITHMETIC OPERATORS
        // Used for basic math: + - * / %
        // ============================================

        int a = 15;
        int b = 4;

        System.out.println("a + b = " + (a + b));   // addition
        System.out.println("a - b = " + (a - b));   // subtraction
        System.out.println("a * b = " + (a * b));   // multiplication
        System.out.println("a / b = " + (a / b));   // division -> integer division, drops decimal! result: 3
        System.out.println("a % b = " + (a % b));   // modulus -> remainder after division, result: 3

        // Careful: dividing two ints gives an int result (truncated), not a decimal
        double preciseDivision = (double) a / b;  // cast one operand to double first
        System.out.println("Precise division: " + preciseDivision);  // result: 3.75


        // ============================================
        // SECTION 2: UNARY OPERATORS
        // Operate on a single operand
        // ============================================

        int x = 10;

        System.out.println("Original x: " + x);
        System.out.println("Negation -x: " + (-x));

        x++;  // post-increment: use current value, then add 1
        System.out.println("After x++: " + x);  // 11

        x--;  // post-decrement: use current value, then subtract 1
        System.out.println("After x--: " + x);  // back to 10

        // Pre vs post increment - the difference matters when used inline
        int y = 5;
        System.out.println("y++ (post, prints THEN increments): " + y++);  // prints 5, y becomes 6
        System.out.println("y is now: " + y);  // 6

        int z = 5;
        System.out.println("++z (pre, increments THEN prints): " + ++z);  // prints 6 directly
        System.out.println("z is now: " + z);  // 6


        // ============================================
        // SECTION 3: ASSIGNMENT OPERATORS
        // Shorthand ways to update a variable's value
        // ============================================

        int num = 10;

        num += 5;   // same as: num = num + 5
        System.out.println("num += 5: " + num);  // 15

        num -= 3;   // same as: num = num - 3
        System.out.println("num -= 3: " + num);  // 12

        num *= 2;   // same as: num = num * 2
        System.out.println("num *= 2: " + num);  // 24

        num /= 4;   // same as: num = num / 4
        System.out.println("num /= 4: " + num);  // 6

        num %= 4;   // same as: num = num % 4
        System.out.println("num %= 4: " + num);  // 2


        // ============================================
        // SECTION 4: RELATIONAL (COMPARISON) OPERATORS
        // Always produce a boolean result (true/false)
        // ============================================

        int p = 10;
        int q = 20;

        System.out.println("p == q: " + (p == q));  // equal to
        System.out.println("p != q: " + (p != q));  // not equal to
        System.out.println("p > q: " + (p > q));    // greater than
        System.out.println("p < q: " + (p < q));    // less than
        System.out.println("p >= q: " + (p >= q));  // greater than or equal to
        System.out.println("p <= q: " + (p <= q));  // less than or equal to


        // ============================================
        // SECTION 5: LOGICAL OPERATORS
        // Combine multiple boolean expressions
        // ============================================

        boolean isAdult = true;
        boolean hasID = false;

        System.out.println("isAdult && hasID: " + (isAdult && hasID));  // AND - both must be true
        System.out.println("isAdult || hasID: " + (isAdult || hasID));  // OR - at least one must be true
        System.out.println("!isAdult: " + (!isAdult));                  // NOT - flips the boolean

        // Short-circuit behavior:
        // In (A && B), if A is false, B is never even evaluated (saves performance)
        // In (A || B), if A is true, B is never even evaluated


        // ============================================
        // SECTION 6: BITWISE OPERATORS
        // Operate directly on the binary representation of numbers
        // Less common day-to-day, but important to recognize
        // ============================================

        int bit1 = 5;   // binary: 0101
        int bit2 = 3;   // binary: 0011

        System.out.println("bit1 & bit2 (AND): " + (bit1 & bit2));   // 0001 -> 1
        System.out.println("bit1 | bit2 (OR): " + (bit1 | bit2));    // 0111 -> 7
        System.out.println("bit1 ^ bit2 (XOR): " + (bit1 ^ bit2));   // 0110 -> 6
        System.out.println("~bit1 (NOT): " + (~bit1));               // flips all bits -> -6
        System.out.println("bit1 << 1 (left shift): " + (bit1 << 1)); // shifts bits left -> 10
        System.out.println("bit1 >> 1 (right shift): " + (bit1 >> 1)); // shifts bits right -> 2


        // ============================================
        // SECTION 7: TERNARY OPERATOR
        // A compact if-else in a single line
        // Syntax: condition ? valueIfTrue : valueIfFalse
        // ============================================

        int age = 20;
        String result = (age >= 18) ? "Adult" : "Minor";
        System.out.println("Ternary result: " + result);

        // Equivalent to:
        // if (age >= 18) {
        //     result = "Adult";
        // } else {
        //     result = "Minor";
        // }


        // ============================================
        // SECTION 8: OPERATOR PRECEDENCE (ORDER OF OPERATIONS)
        // Java follows a strict order, just like math class:
        // 1. Parentheses ()
        // 2. Unary (++, --, !)
        // 3. Multiplicative (*, /, %)
        // 4. Additive (+, -)
        // 5. Relational (<, >, <=, >=)
        // 6. Equality (==, !=)
        // 7. Logical AND (&&)
        // 8. Logical OR (||)
        // 9. Assignment (=, +=, -=, etc.)
        // ============================================

        int precedenceTest = 10 + 5 * 2;         // multiplication happens first: 10 + 10 = 20
        System.out.println("10 + 5 * 2 = " + precedenceTest);

        int precedenceWithParens = (10 + 5) * 2; // parentheses override default order: 15 * 2 = 30
        System.out.println("(10 + 5) * 2 = " + precedenceWithParens);
    }
}