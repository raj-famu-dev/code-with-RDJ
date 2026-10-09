# `_7_Arrays.java`

## Concept
Fixed-size collections — declaring, accessing, looping, common operations, 2D arrays, and the critical reference-vs-copy gotcha.

## Full Line-by-Line Breakdown

### `public class _7_Arrays {`
Declares the class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is An Array?
No code here — just the conceptual framing: an array is a fixed-size container holding multiple values of the **same type**, stored in contiguous memory, accessed by a zero-based index.

---

### SECTION 2: Declaring and Initializing Arrays

**`int[] scores = new int[5];`**
Creates an array that can hold exactly `5` integers. `new int[5]` allocates the memory upfront; all 5 slots automatically start at their default value (`0` for `int`).

**`scores[0] = 90;` through `scores[4] = 88;`**
Fills each slot individually by index. `scores[0]` is the **first** element (not the "zeroth" in casual terms, but literally index `0`).

**`int[] ages = {21, 25, 19, 34, 40};`**
Shorthand — declares the array **and** fills it with values in one line, without needing `new` or specifying a size (Java infers the size from how many values you listed — `5` here).

**`String[] fruits = new String[]{"Apple", "Banana", "Cherry"};`**
A third way to write the same idea as Method 2, but with `new` written explicitly. Functionally identical to the shorthand — this form is occasionally required in certain contexts (like passing an array directly into a method call).

**The three `println` lines**
Print the first element (`index 0`) of each array to confirm they were built correctly.

---

### SECTION 3: Accessing and Modifying Elements

**`ages[2]`**
Since arrays are zero-indexed, index `2` is actually the **third** element — in this array, that's `19`.

**`ages[2] = 20;`**
Directly overwrites the value at index `2`, changing it from `19` to `20`. Arrays are mutable — you can freely reassign individual slots after creation.

**`ages.length`**
Returns how many elements the array holds. Note it's written **without parentheses** — `length` is a **property/field** on arrays, not a method (this differs from `String`'s `.length()`, which *does* use parentheses — a common point of confusion).

---

### SECTION 4: Looping Through Arrays

**`for (int i = 0; i < scores.length; i++) { System.out.println("Index " + i + ": " + scores[i]); }`**
A standard indexed loop — starts at `0`, continues while `i` is less than the array's length, and increments each time. This form gives you access to **both** the index (`i`) and the value (`scores[i]`) at each step.

**`for (String fruit : fruits) { System.out.println(fruit); }`**
The enhanced for-each loop — reads as "for each `fruit` in `fruits`." Simpler syntax, but you lose direct access to the index; you only get each value in turn.

---

### SECTION 5: Common Array Operations

**`int sum = 0;` → `for (int score : scores) { sum += score; }`**
Accumulator pattern: starts at `0`, then adds every element's value to it as the loop walks through the array.

**`double average = (double) sum / scores.length;`**
Casting `sum` to `double` before dividing ensures a precise decimal result rather than truncated integer division (recap from Type Casting).

**`int max = scores[0];` → `for (int score : scores) { if (score > max) { max = score; } }`**
Starts by assuming the **first** element is the largest, then compares every element against the current `max`, updating it whenever a bigger value is found. By the end, `max` holds the true highest value.

**`int min = scores[0];` → (same pattern with `<` instead of `>`)**
Identical logic in reverse — starts assuming the first element is smallest, then updates whenever a smaller value is found.

---

### SECTION 6: The ArrayIndexOutOfBoundsException Gotcha

**The comment about `ages[5]`**
`ages` has `5` elements, meaning valid indices are only `0` through `4`. Attempting `ages[5]` would compile just fine, but **crash at runtime** with an `ArrayIndexOutOfBoundsException` — this is a runtime error, not something the compiler catches in advance.

**`ages[ages.length - 1]`**
The safe, standard pattern for getting an array's **last** element: since `length` is always one more than the highest valid index, subtracting `1` gives you exactly that last valid position — here, index `4`.

---

### SECTION 7: Arrays of Other Types

**`double[] prices = {19.99, 45.50, 12.25};`**
An array holding decimal values instead of integers.

**`boolean[] flags = {true, false, true};`**
An array holding `true`/`false` values.

**`char[] letters = {'J', 'A', 'V', 'A'};`**
An array holding individual characters.

**`letters[0] + letters[1] + letters[2] + letters[3]`**
Concatenates the four `char` values together into one printed String (`"JAVA"`) — proves arrays work identically across every data type, not just `int`.

---

### SECTION 8: 2D Arrays

**`int[][] grid = new int[2][3];`**
Creates a 2D array — think of it as a grid with `2` rows and `3` columns. The double brackets (`[][]`) signal "an array of arrays."

**`grid[0][0] = 1;` through `grid[1][2] = 6;`**
Fills each cell individually — the first bracket is the **row** index, the second is the **column** index.

**`int[][] matrix = { {1, 2, 3}, {4, 5, 6}, {7, 8, 9} };`**
Shorthand — declares and fills a full 3×3 grid in one statement. Each inner `{ }` represents one complete row.

**`grid[1][2]`**
Row index `1` (the second row), column index `2` (the third column) — value `6`.

**`matrix[2][1]`**
Row index `2` (the third row: `{7, 8, 9}`), column index `1` (the second column) — value `8`.

---

### SECTION 9: Looping Through 2D Arrays

**`for (int row = 0; row < matrix.length; row++) { for (int col = 0; col < matrix[row].length; col++) { ... } }`**
Requires **nested loops** — the outer loop walks through each row, and for every row, the inner loop walks through each column within that specific row (`matrix[row].length` gives the number of columns in that row).

**`System.out.print(matrix[row][col] + " ");`**
Note `.print` (not `.println`) — keeps everything on the same line, separated by spaces, until the row is finished.

**`System.out.println();` (empty)**
Called once per completed row, purely to move to the next line before starting the next row's output.

**`for (int[] rowArray : matrix) { for (int value : rowArray) { ... } }`**
The for-each equivalent of the same nested structure — `rowArray` represents one entire row (itself an array), and the inner for-each walks through each individual value inside that row.

---

### SECTION 10: Arrays Are Fixed Size

**`int[] fixedArray = new int[3];`**
Created with a permanent size of `3`.

**The comment about `fixedArray[3]`**
Explains that this would crash — there's no index `3` in a length-3 array (valid indices are only `0`, `1`, `2`). Crucially, there's no way to "grow" this array to hold a fourth element; you would have to create an entirely new, larger array instead. This limitation is exactly what `ArrayList` (covered in `03-collections`) solves.

---

### SECTION 11: Copying Arrays

**`int[] original = {1, 2, 3};`**
The array to be "copied."

**`int[] wrongCopy = original;`**
This does **not** create a second, independent array — it just makes `wrongCopy` point to the **exact same** array in memory as `original`. Both variable names now refer to one single underlying array.

**`wrongCopy[0] = 999;`**
Modifies index `0` — but since `wrongCopy` and `original` are the same array in memory, this change is visible through **either** variable name.

**`original[0]` now printing `999`**
Proves the point: even though only `wrongCopy` was directly modified, `original` shows the same change, because they were never two separate arrays to begin with.

**`int[] realCopy = new int[original.length];` → `for (int i = 0; i < original.length; i++) { realCopy[i] = original[i]; }`**
The **correct** way to copy: manually create a brand-new array of the same length, then loop through and copy each value over individually. This creates a genuinely independent array in its own separate memory.

**`realCopy[0] = 111;` → `original[0]` still prints `999`**
Confirms `realCopy` is truly independent — changing it has zero effect on `original`, unlike the earlier `wrongCopy` scenario.

## Key Rules / Gotchas Recap

- Arrays are zero-indexed — a length-5 array has valid indices `0` through `4`, not `1`