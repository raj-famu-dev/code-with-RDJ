# Project 04 — Student Grade Management System

## 📌 Project Description

A console-based Java application that allows a user to manage a class of students and their academic scores across three subjects (Math, Physics, Biology). The program runs as a continuous menu-driven loop, letting the user add students, view all recorded students in a formatted table, search for a specific student, and view overall class statistics — all without ever crashing on bad input.

This project was built as a **capstone exercise for `01-basics`** — it deliberately requires combining every foundational Java concept into one working, cohesive program rather than practicing each concept in isolation.

---

## 📋 Requirements

### Functional Requirements
1. **Add Student** — capture a name and 3 subject scores; reject empty names and out-of-range/non-numeric scores without crashing
2. **View All Students** — display every student in a neatly aligned table, including their calculated average
3. **Search Student by Name** — case-insensitive lookup; show full details if found, a clear message if not
4. **Class Statistics** — show total student count, class average, top performer, and lowest performer
5. **Exit** — clean shutdown, closing any open resources

### Non-Functional Requirements
- No unhandled crashes on any bad input
- Menu must loop continuously until the user explicitly exits
- Output must be aligned/formatted, not raw unaligned print statements
- Logic must be broken into well-named methods, not crammed into `main()`

---

## 🗂 Full Code Walkthrough

### Imports and Class Declaration

```java
import java.util.Scanner;
public class StudentGradeManager {
```
Imports `Scanner` for reading console input. The class name matches the filename, as required by Java.

### Shared Storage Fields

```java
static final int MAX_STUDENTS = 50;
static String[] names = new String[MAX_STUDENTS];
static int[][] scores = new int[MAX_STUDENTS][3];
static int studentCount = 0;
static Scanner scanner = new Scanner(System.in);
```

| Line | Purpose |
|---|---|
| `MAX_STUDENTS` | A shared, unchangeable constant (`static final`) capping storage at 50 students |
| `names[]` | A `String` array — one slot per student, holding their name |
| `scores[][]` | A **2D array** — each row belongs to one student, and holds exactly 3 subject scores (columns) |
| `studentCount` | Tracks how many slots are actually filled — since arrays are fixed-size, this tells the rest of the program where the "real" data ends |
| `scanner` | A single shared `Scanner`, created once and reused everywhere input is needed |

**Why this satisfies the requirements:** `names[]` and `scores[][]` are **parallel arrays** — index `i` in both arrays always describes the *same* student. This is the chosen data structure for "how will you store multiple students' data," directly required by the project brief.

---

### `main()` — The Program Loop

```java
public static void main(String[] args) {
    boolean running = true;

    do {
        printMenu();
        int choice = readMenuChoice();

        switch (choice) {
            case 1 -> addStudent();
            case 2 -> viewAllStrudents();
            case 3 -> searchStudent();
            case 4 -> classStatistics();
            case 5 -> {
                System.out.println("Goodbye!");
                running = false;
            }
            default -> System.err.println("Invalid Option. Try again!");
        }
        System.out.println();
    } while (running);

    scanner.close();
}
```

**Line-by-line:**
- `boolean running = true;` — a flag controlling the loop; starts `true` so the menu always shows at least once
- `do { ... } while (running);` — a **do-while loop**, guaranteeing the menu prints before the exit condition is even checked (fulfills: *"menu must show at least once, then loop until exit"*)
- `printMenu();` — displays the options (defined further down)
- `int choice = readMenuChoice();` — safely captures the user's numeric choice (see below)
- The `switch` (modern arrow-style expression) routes to the correct method based on `choice`
- `case 5 -> { ... running = false; }` — sets the loop flag to `false`, which is checked at the bottom of the `do-while`, ending the loop naturally on the *next* check
- `System.err.println(...)` in `default` — prints to the **error stream** (shows red in most IDEs) specifically for invalid menu input, distinguishing it from normal output
- `scanner.close();` — releases the Scanner's resources once the loop has fully ended

**Requirement fulfilled:** *"The menu must loop until the user explicitly exits — it should never show only once."* The `do-while` structure guarantees this by design.

---

### `printMenu()` — Menu Display

```java
static void printMenu() {
    System.out.println("=========================================");
    System.out.println("   STUDENT GRADE MANAGEMENT SYSTEM");
    System.out.println("=========================================");
    System.out.println("1. Add Student");
    System.out.println("2. View All Students");
    System.out.println("3. Search Student by Name");
    System.out.println("4. Class Statistics (avg/highest/lowest)");
    System.out.println("5. Exit");
    System.out.print("Choose an option (1-5): ");
}
```
A simple `void` method — prints text only, returns nothing. The final line uses `.print()` instead of `.println()` so the user's typed input appears right after the colon on the same line, rather than on a new one.

---

### `readMenuChoice()` — Safe Menu Input

```java
static int readMenuChoice() {
    if (scanner.hasNextInt()) {
        int choice = scanner.nextInt();
        scanner.nextLine();
        return choice;
    } else {
        scanner.next();
        scanner.nextLine();
        return -1;
    }
}
```

**Line-by-line:**
- `scanner.hasNextInt()` — checks **without consuming** whether the next input is actually a valid integer
- If true: reads it with `.nextInt()`, then immediately calls `.nextLine()` to consume the leftover newline character left behind (the classic `nextInt()`/`nextLine()` buffer bug from `_10_UserInput.java`)
- If false: the input wasn't a number at all (e.g., the user typed a letter). `.next()` consumes that invalid token so it doesn't get stuck in the buffer, `.nextLine()` clears any remaining leftover, and `-1` is returned — a value that will never match any real menu case, so it safely falls through to the `default` branch in `main()`'s switch

**Requirement fulfilled:** *"If I type a letter instead of a number for a score/menu choice, does the program recover instead of crashing?"* — Yes, this method is exactly why: bad input is detected and safely defused before it can throw an `InputMismatchException`.

---

### `addStudent()` — Adding a New Student

```java
static void addStudent() {
    if (studentCount >= MAX_STUDENTS) {
        System.out.println("Cannot add more students - storage is full.");
        return;
    }

    System.out.println("Enter student name: ");
    String name = scanner.nextLine().trim();

    if (name.isEmpty()) {
        System.out.println("name cannot be empty. Student not added.");
        return;
    }

    int[] subjectScores = new int[3];
    String[] subjects = {"Math", "Physics", "Biology"};

    for (int i = 0; i < subjects.length; i++) {
        subjectScores[i] = readValidScore(subjects[i]);
    }

    names[studentCount] = name;
    scores[studentCount] = subjectScores;
    studentCount++;

    System.out.println("Student '" + name + "' added successfully.");
}
```

**Line-by-line:**
- `if (studentCount >= MAX_STUDENTS) { ...; return; }` — guards against overflowing the fixed-size arrays; an **early return** exits the method immediately if storage is full, satisfying *"decide a reasonable limit and handle the case where it's exceeded"*
- `scanner.nextLine().trim()` — reads the full name (allowing spaces, e.g., "John Smith"), then `.trim()` strips any accidental leading/trailing whitespace
- `if (name.isEmpty()) { ...; return; }` — rejects a blank name, satisfying the *"reject a blank/empty name"* requirement, again via early return
- `String[] subjects = {"Math", "Physics", "Biology"};` — defines the 3 subject labels once, used both for prompting and for looping
- The `for` loop calls `readValidScore(...)` once per subject, storing each validated result into `subjectScores[i]`
- `names[studentCount] = name;` / `scores[studentCount] = subjectScores;` — writes the new student's data into the **next free slot** in the parallel arrays
- `studentCount++;` — advances the counter, marking that slot as now "used" and pointing to the next free one for the future

**Requirement fulfilled:** Covers the entire "Add Student" functional requirement — empty-name rejection, full-storage rejection, and correctly storing valid data — all in one method.

---

### `readValidScore()` — Validated Score Input

```java
static int readValidScore(String subjectName) {
    int score;
    while (true) {
        System.out.println("Enter " + subjectName + " score (0-100): ");
        if (scanner.hasNextInt()) {
            score = scanner.nextInt();
            scanner.nextLine();
            if (score >= 0 && score <= 100) {
                return score;
            } else {
                System.out.println("Score must be between 0 and 100.");
            }
        } else {
            System.out.println("That's not a number.");
            scanner.next();
            scanner.nextLine();
        }
    }
}
```

**Line-by-line:**
- `while (true) { ... }` — an **intentional infinite loop**; it only ever ends via the `return score;` statement buried inside — a controlled, safe pattern (recap from `_6_Loops.java`)
- Each iteration re-prompts for the *same* subject's score until a valid one is entered
- `scanner.hasNextInt()` check — same non-numeric-input defense as `readMenuChoice()`
- `score >= 0 && score <= 100` — a **logical AND**, requiring both bounds to hold simultaneously; anything outside this range prints an error and loops again *without* returning
- Only a genuinely valid score (numeric AND within range) triggers `return score;`, breaking out of the loop

**Requirement fulfilled:** *"Reject any score outside 0-100 — keep re-prompting until valid"* and *"reject non-numeric input — keep re-prompting without crashing"* — both handled directly by this method's loop-and-validate structure.

---

### `viewAllStrudents()` — Displaying All Students

```java
static void viewAllStrudents() {
    if (studentCount == 0) {
        System.out.println("No students recorded yet.");
        return;
    }
    System.out.printf("%-15s %8s %8s %8s %10s%n", "Name", "Math", "Science", "English", "Average");
    System.out.println("-".repeat(55));

    for (int i = 0; i < studentCount; i++) {
        double average = calculateAverage(scores[i]);
        System.out.printf("%-15s %8d %8d %8d %10.2f%n",
                names[i], scores[i][0], scores[i][1], scores[i][2], average);
    }
}
```

**Line-by-line:**
- `if (studentCount == 0) { ...; return; }` — guards against printing a table with zero rows; satisfies *"if no students exist, print a friendly message instead of an empty table"*
- `System.out.printf("%-15s %8s %8s %8s %10s%n", ...)` — prints the **header row**: `%-15s` left-aligns the "Name" column in a 15-character field; each `%8s` right-aligns a subject header in an 8-character field; `%10s` right-aligns "Average" in 10 characters
- `"-".repeat(55)` — prints a 55-character dashed line as a visual divider under the header
- The `for` loop iterates only up to `studentCount` (not the full array length), since only that many slots actually hold real data
- `calculateAverage(scores[i])` — calls a separate method to compute each student's average (see below)
- `%10.2f` — formats the average to **exactly 2 decimal places**, right-aligned in a 10-character field

**Requirement fulfilled:** *"Display every student in a neatly aligned table"* — the combination of fixed-width specifiers (`%-15s`, `%8d`, `%10.2f`) guarantees every row lines up under the header regardless of name length or score digit count.

---

### `calculateAverage()` — Average Calculation

```java
static double calculateAverage(int[] studentScores) {
    int sum = 0;
    for (int score : studentScores) {
        sum += score;
    }
    return (double) sum / studentScores.length;
}
```

**Line-by-line:**
- `int sum = 0;` — an accumulator, starting at zero
- `for (int score : studentScores) { sum += score; }` — a **for-each loop**, adding every score in the array to the running total
- `(double) sum / studentScores.length` — casts `sum` to `double` **before** dividing; without this cast, `int / int` would perform integer division and silently truncate the result (e.g., `255 / 3` would still correctly give `85`, but a case like `256 / 3` would wrongly give `85` instead of `85.33`)

**Requirement fulfilled:** *"The average must be calculated correctly (watch out for integer division)"* — this is precisely the bug this cast prevents.

---

### `assignGrade()` — Letter Grade Assignment

```java
static char assignGrade(double average) {
    if (average >= 90) return 'A';
    else if (average >= 80) return 'B';
    else if (average >= 70) return 'C';
    else if (average >= 60) return 'D';
    else return 'F';
}
```

An **if-else-if chain**, checked top to bottom. Since each branch has a `return`, the method exits immediately once a matching condition is found — no `break` needed, and only one letter is ever returned per call.

**Requirement fulfilled:** *"Design your own grade boundaries"* — a self-defined 90/80/70/60 cutoff scale, applied consistently everywhere a grade is needed (search results and class statistics both reuse this same method).

---

### `searchStudent()` — Searching By Name

```java
static void searchStudent() {
    if (studentCount == 0) {
        System.out.println("No students to search.");
        return;
    }

    System.out.print("Enter name to search: ");
    String query = scanner.nextLine().trim();

    boolean found = false;
    for (int i = 0; i < studentCount; i++) {
        if (names[i].equalsIgnoreCase(query)) {
            double avg = calculateAverage(scores[i]);
            char grade = assignGrade(avg);

            System.out.println("--- Student Found ---");
            System.out.println("Name: " + names[i]);
            System.out.printf("Math: %d | Science: %d | English: %d%n",
                    scores[i][0], scores[i][1], scores[i][2]);
            System.out.printf("Average: %.2f | Grade: %c%n", avg, grade);

            found = true;
            break;
        }
    }

    if (!found) {
        System.out.println("No student found with that name.");
    }
}
```

**Line-by-line:**
- Empty-list guard clause, same pattern as `viewAllStrudents()`
- `names[i].equalsIgnoreCase(query)` — a **case-insensitive** String comparison (recap from `_8_Strings.java`); searching `"alice"` correctly matches a stored `"Alice"`
- Once a match is found: prints the full record, computes the average and grade via the same two helper methods used elsewhere (no duplicated logic)
- `found = true; break;` — marks the match and **immediately exits the loop** — there's no need to keep scanning once the target is found
- `if (!found) { ... }` — the **logical NOT** checks whether the loop completed without ever finding a match, printing a clear "not found" message in that case

**Requirement fulfilled:** *"Case-insensitive... stop searching once found... clear not-found message"* — all three conditions satisfied directly by this structure.

---

### `classStatistics()` — Aggregate Class Data

```java
static void classStatistics() {
    if (studentCount == 0) {
        System.out.println("No students recorded yet.");
        return;
    }

    double totalOfAverages = 0;
    double highestAvg = calculateAverage(scores[0]);
    double lowestAvg = calculateAverage(scores[0]);
    String topStudent = names[0];
    String bottomStudent = names[0];

    for (int i = 0; i < studentCount; i++) {
        double avg = calculateAverage(scores[i]);
        totalOfAverages += avg;

        if (avg > highestAvg) {
            highestAvg = avg;
            topStudent = names[i];
        }
        if (avg < lowestAvg) {
            lowestAvg = avg;
            bottomStudent = names[i];
        }
    }

    double classAverage = totalOfAverages / studentCount;

    System.out.println("--- Class Statistics ---");
    System.out.printf("Total students: %d%n", studentCount);
    System.out.printf("Class average: %.2f (Grade: %c)%n",
            classAverage, assignGrade(classAverage));
    System.out.printf("Top performer: %s (%.2f)%n", topStudent, highestAvg);
    System.out.printf("Needs support: %s (%.2f)%n", bottomStudent, lowestAvg);
}
```

**Line-by-line:**
- Empty-list guard clause, same pattern as before
- `highestAvg`, `lowestAvg`, `topStudent`, `bottomStudent` are all **seeded with student index 0's data** — a standard "assume the first is both the max and min, then prove otherwise" pattern (recap from `_7_Arrays.java`'s min/max logic)
- Inside the loop: `totalOfAverages += avg;` accumulates a running sum of every student's average, used later to compute the overall class average
- Two separate `if` checks (not `if-else`) compare the current student's average against both the running highest and running lowest independently, updating each and its associated name whenever a new record is found
- `classAverage = totalOfAverages / studentCount;` — the **average of averages**, giving an overall class performance figure
- The final block prints total count, class average with its letter grade, and both the top and bottom performer with their names and figures

**Requirement fulfilled:** *"Total students, class average, top performer, lowest performer... if no students exist, print a friendly message"* — every listed statistic is computed and displayed, with the guard clause preventing this from running on an empty dataset (which would otherwise crash on `scores[0]` with no students present).

---

## ✅ Self-Check Against Original Requirements

| Requirement | How It's Met |
|---|---|
| Menu loops until exit | `do-while` loop in `main()`, controlled by `running` flag |
| Reject empty/blank name | `if (name.isEmpty())` guard in `addStudent()` |
| Reject invalid scores | `readValidScore()`'s `while(true)` retry loop with range + numeric checks |
| No crashes on bad input | `hasNextInt()` checks before every `nextInt()` call, throughout |
| Aligned table output | Fixed-width `printf` specifiers in `viewAllStrudents()` |
| Case-insensitive search | `.equalsIgnoreCase()` in `searchStudent()` |
| Stop searching once found | `break` immediately after a match |
| Correct average (no truncation) | `(double)` cast before division in `calculateAverage()` |
| Class statistics complete | `classStatistics()` computes count, class average, top, and bottom performer |
| Broken into methods | Every feature is its own named method; `main()` only orchestrates the loop and menu routing |
| Clean exit | `case 5` sets `running = false`; `scanner.close()` called once the loop ends |

---

## 🐛 Known Naming Note

The method `viewAllStrudents()` contains a typo (`Strudents` instead of `Students`) carried over from an early draft — functionally harmless since Java doesn't care about spelling, but worth renaming to `viewAllStudents()` for a cleaner, more professional-looking codebase before considering this "done." The header row inside that same method also still prints `"Science"` and `"English"` as column labels, even though the actual subjects tracked are Math, Physics, and Biology — worth fixing those three header strings to match the real data.

## 🚀 Possible Extensions

- Add a "delete student" option (requires shifting array elements)
- Support a variable number of subjects instead of a hardcoded 3
- Sort students by average before displaying the table