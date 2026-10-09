public class _2_Constructors {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS A CONSTRUCTOR?
        // A special method that runs AUTOMATICALLY when an object is created
        // with 'new'. Its job is to initialize the object's fields.
        // Rules: same name as the class, NO return type (not even void)
        // ============================================


        // ============================================
        // SECTION 2: DEFAULT CONSTRUCTOR
        // If you write NO constructor at all, Java silently provides an
        // empty one for you (fields just get their default values: 0, null, false)
        // ============================================

        Book book1 = new Book();  // uses Java's auto-generated default constructor
        System.out.println("Book 1 (default constructor): title=" + book1.title +
                ", pages=" + book1.pages);


        // ============================================
        // SECTION 3: PARAMETERIZED CONSTRUCTOR
        // Once you write your OWN constructor, Java stops auto-generating
        // the default one. You must set fields explicitly via parameters.
        // ============================================

        Book book2 = new Book("Atomic Habits", 320);
        System.out.println("Book 2 (parameterized): title=" + book2.title +
                ", pages=" + book2.pages);


        // ============================================
        // SECTION 4: CONSTRUCTOR OVERLOADING
        // Multiple constructors, same class, different parameter lists -
        // Java picks the right one based on what arguments you pass
        // ============================================

        Book book3 = new Book("Deep Work");  // uses the (String) constructor
        Book book4 = new Book("Sapiens", 443, "Yuval Noah Harari");  // uses the 3-param one

        System.out.println("Book 3 (title only): title=" + book3.title + ", pages=" + book3.pages);
        System.out.println("Book 4 (full details): title=" + book4.title +
                ", pages=" + book4.pages + ", author=" + book4.author);


        // ============================================
        // SECTION 5: THE 'this' KEYWORD IN CONSTRUCTORS
        // When a parameter name is the SAME as a field name, 'this.fieldName'
        // refers to the object's field, while the plain name refers to the parameter.
        // Without 'this', Java would just assign the parameter to itself - a common bug!
        // ============================================

        // See the Book class below - notice 'this.title = title;' pattern


        // ============================================
        // SECTION 6: CONSTRUCTOR CHAINING WITH this(...)
        // A constructor can call ANOTHER constructor in the SAME class,
        // to avoid repeating the same initialization logic multiple times
        // MUST be the very first line in the constructor if used
        // ============================================

        Book book5 = new Book("Unknown Title");  // this constructor internally chains
        System.out.println("Book 5 (chained default pages): title=" + book5.title +
                ", pages=" + book5.pages);


        // ============================================
        // SECTION 7: WHY CONSTRUCTORS MATTER (COMPARISON TO SECTION 1 CLASS)
        // In _1_ClassesAndObjects, we had to manually set every field
        // AFTER creating the object (car1.brand = "Toyota"; etc).
        // Constructors let us set everything in ONE line, at creation time -
        // and can ENFORCE that required fields are never accidentally left unset.
        // ============================================

        Book betterBook = new Book("Clean Code", 464, "Robert C. Martin");
        System.out.println("Fully initialized in one line: " + betterBook.title +
                " by " + betterBook.author + " (" + betterBook.pages + " pages)");
    }
}


// ============================================
// THE CLASS DEFINITION WITH MULTIPLE CONSTRUCTORS
// ============================================

class Book {

    String title;
    int pages;
    String author;

    // --- Constructor 1: No-argument (explicit version of what Java auto-generates) ---
    // Once ANY constructor is written, Java stops providing the free default one,
    // so if you still want a no-arg option, you must write it yourself
    Book() {
        title = "Untitled";
        pages = 0;
        author = "Unknown";
        System.out.println("[No-arg constructor called]");
    }

    // --- Constructor 2: Title only ---
    Book(String title) {
        this(title, 100);  // CHAINS to the 2-param constructor below, must be first line
        System.out.println("[Title-only constructor called, chained to 2-param version]");
    }

    // --- Constructor 3: Title and pages ---
    Book(String title, int pages) {
        this.title = title;   // 'this.title' = the field, 'title' = the parameter
        this.pages = pages;
        this.author = "Unknown";
        System.out.println("[Title+pages constructor called]");
    }

    // --- Constructor 4: Full details ---
    Book(String title, int pages, String author) {
        this.title = title;
        this.pages = pages;
        this.author = author;
        System.out.println("[Full constructor called]");
    }
}