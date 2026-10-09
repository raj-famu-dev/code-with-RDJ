# `_2_Constructors.java`

## Concept
Constructors — special methods that run automatically at object creation to initialize fields, including default constructors, parameterized constructors, overloading, and constructor chaining.

## Full Line-by-Line Breakdown

### `public class _2_Constructors {`
Declares the main class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is A Constructor?
No executable code here — just the conceptual framing. A constructor is a special method that runs **automatically** the moment `new` creates an object. Its rules: it must share the class's exact name, and it has **no return type at all** — not even `void`.

---

### SECTION 2: Default Constructor

**`Book book1 = new Book();`**
Calls `Book`'s no-argument constructor. Since one was explicitly written in the class (see below), this is technically no longer Java's *auto-generated* default — but it behaves the same way conceptually: no arguments needed.

**`book1.title` / `book1.pages`**
Print `"Untitled"` and `0` — the values this particular constructor explicitly assigns.

---

### SECTION 3: Parameterized Constructor

**`Book book2 = new Book("Atomic Habits", 320);`**
Calls the constructor matching **two arguments** (a `String` and an `int`) — Java picks `Book(String title, int pages)` based on this exact argument signature.

**`book2.title` / `book2.pages`**
Print `"Atomic Habits"` and `320` — the values passed in directly at creation time, rather than being set field-by-field afterward.

---

### SECTION 4: Constructor Overloading

**`Book book3 = new Book("Deep Work");`**
Only **one** argument is passed — Java matches this to the `Book(String title)` constructor specifically.

**`Book book4 = new Book("Sapiens", 443, "Yuval Noah Harari");`**
**Three** arguments — matches the `Book(String title, int pages, String author)` constructor instead.

**The two `println` lines**
Confirm each object was built using a **different** constructor, based purely on how many arguments were supplied when calling `new Book(...)`. This is the same overloading principle from `_9_Methods.java`, applied to constructors specifically.

---

### SECTION 5: The `this` Keyword In Constructors
No new code here — just a pointer back to the class definition below, where `this.title = title;` resolves the naming conflict between the field `title` and the parameter also named `title`.

---

### SECTION 6: Constructor Chaining With `this(...)`

**`Book book5 = new Book("Unknown Title");`**
Calls the single-argument constructor `Book(String title)`.

**Inside that constructor:** `this(title, 100);`
This line **calls another constructor in the same class** — specifically `Book(String title, int pages)` — passing along `title` and a default value of `100` for pages. This must be the **very first line** in the constructor if used at all.

**`book5.title` / `book5.pages`**
Print `"Unknown Title"` and `100` — proving the chain actually ran and supplied the default page count, even though `book5`'s constructor call itself never mentioned a page number.

---

### SECTION 7: Why Constructors Matter (Comparison)

**`Book betterBook = new Book("Clean Code", 464, "Robert C. Martin");`**
A direct contrast to `_1_ClassesAndObjects.java`, where fields had to be set individually **after** creating the object (`car1.brand = "Toyota";` etc., across multiple lines). Here, all three fields are set correctly in **one single line**, at the exact moment the object is created — and there's no way to accidentally forget to set one, since the constructor requires all three arguments.

---

### The `Book` Class Definition (Below `main`)

**Fields:**
```java
String title;
int pages;
String author;
```
The state every `Book` object will hold.

**Constructor 1 — No-argument:**
```java
Book() {
    title = "Untitled";
    pages = 0;
    author = "Unknown";
    System.out.println("[No-arg constructor called]");
}
```
Explicitly written here (not Java's silent auto-generated version) — necessary because once **any** constructor is written in a class, Java stops providing the free no-arg one automatically. If you still want `new Book()` to work, you must write this version yourself.

**Constructor 2 — Title only:**
```java
Book(String title) {
    this(title, 100);
    System.out.println("[Title-only constructor called, chained to 2-param version]");
}
```
Rather than repeating field-assignment logic, this delegates to Constructor 3 via `this(title, 100)`, supplying a sensible default page count.

**Constructor 3 — Title and pages:**
```java
Book(String title, int pages) {
    this.title = title;
    this.pages = pages;
    this.author = "Unknown";
    System.out.println("[Title+pages constructor called]");
}
```
`this.title` refers to the **field**; the plain `title` refers to the **parameter**. Without the `this.` prefix, writing `title = title;` would just assign the parameter to itself, leaving the actual field untouched — a subtle, easy-to-miss bug.

**Constructor 4 — Full details:**
```java
Book(String title, int pages, String author) {
    this.title = title;
    this.pages = pages;
    this.author = author;
    System.out.println("[Full constructor called]");
}
```
The most complete version — sets all three fields directly from arguments, no defaults or chaining needed.

**The bracketed `[... constructor called]` print statements**
Each constructor includes one of these purely so you can watch the console output and confirm **exactly** which constructor ran for each object — especially useful for seeing the chaining in Section 6 actually happen (you'll see both the title-only message AND the title+pages message print for `book5`, proving the chain occurred).

## Key Rules / Gotchas Recap

- Writing **any** constructor removes Java's free default (no-arg) constructor — you must write one yourself if you still want `new Book()` to work
- Constructor overloading is resolved the same way method overloading is: by argument count/type, at compile time
- `this(...)` must be the **very first statement** in a constructor if used — nothing can come before it
- Without `this.fieldName`, a constructor parameter with the same name as a field would just assign to itself, silently leaving the actual field at its default value

## Why This Structure Exists

Constructors solve exactly the problem demonstrated in `_1_ClassesAndObjects.java` — manually setting every field after creating an object is error-prone and easy to forget. Constructors guarantee an object starts in a valid, fully-initialized state the moment `new` runs, and overloading/chaining let you offer multiple convenient ways to create that object without duplicating initialization logic.