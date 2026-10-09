# `_9_Methods.java`

## Concept
Reusable blocks of code — parameters, return types, overloading, pass-by-value behavior, varargs, and recursion.

## Full Line-by-Line Breakdown

### `public class _9_Methods {`
Declares the class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is A Method?

**`greetUser();`**
Calls a method **defined below**, outside of `main()` but still inside the same class. Java doesn't require methods to be defined *before* they're called, as long as they exist somewhere in the class — the compiler reads the whole class before running anything.

---

### SECTION 2: Methods With Parameters

**`greetByName("RDJ");` / `greetByName("Anthropic");`**
Calls the same method twice with **different arguments**. The word inside the quotes is passed **into** the method as data, letting one method definition handle many different inputs.

---

### SECTION 3: Methods With Return Values

**`int sum = addNumbers(5, 10);`**
Calls `addNumbers`, passing `5` and `10` in. The method **returns** a value (`15`), which gets stored directly into the `sum` variable.

**`double average = calculateAverage(85, 92, 78);`**
Same idea — calls a method, captures its returned value into `average`.

---

### SECTION 4: Methods With Multiple Parameters

**`printProfile("RDJ", 25, true);`**
Passes three arguments of **different types** (`String`, `int`, `boolean`) in one call — proves a method can accept multiple parameters of mixed types, as long as the method's own definition matches that same order and types.

---

### SECTION 5: Method Overloading

**`add(3, 4)`**
Java looks at the arguments (`two ints`) and matches them to the `add(int a, int b)` version — returns `7`.

**`add(3, 4, 5)`**
Three ints matches `add(int a, int b, int c)` instead — returns `12`.

**`add(3.5, 4.5)`**
Two doubles matches `add(double a, double b)` — returns `8.0`.

**`add("Hello", "World")`**
Two Strings matches `add(String a, String b)` — returns `"Hello World"` (concatenation, not addition, since these are Strings).

**The key concept:** all four methods share the exact same name (`add`), but Java determines **which one to call** purely by looking at the number and types of arguments provided — this is resolved at **compile time**.

---

### SECTION 6: void vs Return Type Methods

**`printMessage("This method returns nothing");`**
Calls a `void` method — it performs an action (printing) but gives nothing back to store in a variable.

**`String result = buildMessage("This method returns a value");`**
Calls a method that **does** return something (a `String`), which gets captured into `result` and then printed separately.

---

### SECTION 7: Pass By Value

**`int originalNumber = 10;`**
The original variable.

**`modifyValue(originalNumber);`**
Passes `originalNumber`'s **value** (`10`) into the method — but only a **copy** of that value goes in, not the variable itself.

**Inside `modifyValue`:** `value = value + 100;`
This changes the **local copy** (`value`) to `110`, but this has zero effect on `originalNumber` back in `main()`, since they were never connected — `value` was just handed a copy of the number `10`.

**`originalNumber` still printing `10` afterward**
Proves the point directly — the original variable in `main()` is completely unaffected by what happened inside the method.

---

### SECTION 8: Pass By Value With Arrays (The Exception)

**`int[] numbers = {1, 2, 3};`**
An array — remember, arrays are **objects**, not primitives.

**`modifyArray(numbers);`**
Passes `numbers` into the method. What's actually copied here is the **reference** (the "address" pointing to the array) — not the array's contents themselves. So the method's parameter (`arr`) and the original `numbers` variable both end up pointing to the **exact same array in memory**.

**Inside `modifyArray`:** `arr[0] = 999;`
Modifies index `0` of the array **that `arr` points to** — but since `arr` and `numbers` point to the same underlying array, this change is visible through `numbers` too.

**`numbers[0]` now printing `999`**
Confirms this — unlike the primitive example in Section 7, this change **does** persist outside the method, because arrays are reference types.

---

### SECTION 9: Varargs

**`sumAll(1, 2)`**
Calls the method with 2 arguments.

**`sumAll(1, 2, 3, 4, 5)`**
Calls the **same** method with 5 arguments.

**`sumAll()`**
Calls it with **zero** arguments.

**The varargs parameter `int... nums`**
The `...` syntax means "accept any number of `int` arguments, from zero upward." Inside the method, `nums` is treated just like a regular array — you can loop through it with a for-each, regardless of how many values were actually passed in when it was called.

---

### SECTION 10: Recursion

**`factorial(5)`**
Calls the method with `5`.

**Inside `factorial`:**
```java
if (n <= 1) {
    return 1;
}
return n * factorial(n - 1);
```
This method **calls itself**, but with a smaller input each time (`n - 1`). The `if (n <= 1) { return 1; }` line is the **base case** — the condition that eventually stops the recursion. Without it, the method would keep calling itself forever, eventually crashing with a `StackOverflowError`.

**Tracing through `factorial(5)`:**
`5 * factorial(4)` → `5 * (4 * factorial(3))` → `5 * (4 * (3 * factorial(2)))` → `5 * (4 * (3 * (2 * factorial(1))))` → and since `factorial(1)` hits the base case and returns `1`, everything unwinds back up: `5 * 4 * 3 * 2 * 1 = 120`.

---

### The Method Definitions (Below `main()`)

**`static void greetUser() { System.out.println("Welcome to Java Methods!"); }`**
No parameters, no return value — just performs an action.

**`static void greetByName(String userName) { System.out.println("Hello, " + userName + "!"); }`**
Accepts one `String` parameter, uses it inside the printed message.

**`static int addNumbers(int a, int b) { return a + b; }`**
Accepts two `int`s, returns their sum as an `int`. The `return` type in the method signature (`int`) must match what's actually returned.

**`static double calculateAverage(int a, int b, int c) { return (a + b + c) / 3.0; }`**
Note the `3.0` (not just `3`) — this forces the division to be a `double` calculation, avoiding integer division truncation (recap from Type Casting and Operators).

**`static void printProfile(String name, int age, boolean isActive) { ... }`**
Three parameters of different types, all used together inside one formatted print statement.

**The four overloaded `add` methods**
Each has the exact same name but a different **signature** (parameter count and/or types) — this is what makes overloading valid; Java would reject two methods with the identical name **and** identical parameter list.

**`static void printMessage(String msg) { System.out.println(msg); }`**
A `void` method — performs the print action directly, returns nothing.

**`static String buildMessage(String msg) { return "Built message: " + msg; }`**
Returns a new `String` built from the input, rather than printing it directly — the caller decides what to do with the result.

**`static void modifyValue(int value) { value = value + 100; ... }`**
Demonstrates pass-by-value with a primitive — reassigning `value` inside only affects this method's local copy.

**`static void modifyArray(int[] arr) { arr[0] = 999; }`**
Demonstrates the array exception — modifying an **element** of the array (not reassigning the whole array itself) affects the original array back in the caller, since both share the same reference.

**`static int sumAll(int... nums) { int total = 0; for (int n : nums) { total += n; } return total; }`**
Loops through however many values were passed in (`nums`, treated as an array), accumulating their sum.

**`static int factorial(int n) { if (n <= 1) { return 1; } return n * factorial(n - 1); }`**
The recursive method — calls itself with a progressively smaller `n` until it hits the base case.

## Key Rules / Gotchas Recap

- Method overloading is resolved by the compiler based on argument count/types — same name, different signature is required
- `void` methods perform actions but return nothing; any other declared return type **must** return a matching value
- Java is always pass-by-value — but for arrays/objects, the "value" being copied is a **reference**, so modifying the object's *contents* (not reassigning the whole object) still affects the original outside the method
- Varargs (`type... name`) let a method accept zero or more arguments of one type, treated internally like an array
- Recursion **requires** a base case to stop, or it crashes with a `StackOverflowError`

## Why This Structure Exists

Methods are the first real step toward organizing code into reusable, testable units — instead of writing the same logic over and over, you isolate it once and call it wherever needed. This is the direct conceptual bridge into `02-oop`, where methods become the *behavior* half of objects, paired with fields as the *data* half.