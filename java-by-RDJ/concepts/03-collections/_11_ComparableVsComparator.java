// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.*;

public class _11_ComparableVsComparator {

    // Comparable: the class itself defines its ONE natural order (here: by name)
    record Student(String name, int grade, double gpa) implements Comparable<Student> {
        @Override
        public int compareTo(Student other) {
            return name.compareTo(other.name);
        }
    }

    public static void main(String[] args) {

        List<Student> students = new ArrayList<>(List.of(
                new Student("Maya", 10, 3.5),
                new Student("Ben", 11, 3.9),
                new Student("Ava", 10, 3.9),
                new Student("Zoe", 11, 3.2)));


        // ============================================
        // SECTION 1: Comparable = THE NATURAL ORDER
        // compareTo returns: negative (this comes first), 0 (equal), positive (this comes later).
        // Once a class is Comparable, sort() and TreeSet work with no extra help.
        // ============================================

        Collections.sort(students);
        System.out.println("Natural order (by name):");
        students.forEach(s -> System.out.println("  " + s));


        // ============================================
        // SECTION 2: Comparator = AN ORDER CHOSEN FROM OUTSIDE
        // Use it for a different order, or when you cannot edit the class.
        // You can have as many Comparators as you like.
        // ============================================

        students.sort(Comparator.comparingDouble(Student::gpa));
        System.out.println("By GPA ascending:");
        students.forEach(s -> System.out.println("  " + s));


        // ============================================
        // SECTION 3: CHAINING - tie-breakers
        // Grade ascending, then GPA descending, then name.
        // ============================================

        Comparator<Student> ranking = Comparator.comparingInt(Student::grade)
                .thenComparing(Student::gpa, Comparator.reverseOrder())
                .thenComparing(Student::name);
        students.sort(ranking);
        System.out.println("Grade, then GPA high-to-low, then name:");
        students.forEach(s -> System.out.println("  " + s));

        students.sort(ranking.reversed());
        System.out.println("Reversed ranking, first = " + students.get(0).name());


        // ============================================
        // SECTION 4: nullsFirst / nullsLast
        // ============================================

        List<String> withNull = new ArrayList<>(Arrays.asList("b", null, "a"));
        withNull.sort(Comparator.nullsFirst(Comparator.naturalOrder()));
        System.out.println("nullsFirst: " + withNull);


        // ============================================
        // SECTION 5: TRAP - COMPARING WITH SUBTRACTION
        // (a, b) -> a - b looks fine until the numbers are large or negative:
        // the subtraction overflows and flips the sign.
        // ============================================

        Comparator<Integer> bad = (a, b) -> a - b;
        int wrong = bad.compare(Integer.MAX_VALUE, -1);
        int right = Integer.compare(Integer.MAX_VALUE, -1);
        System.out.println("Subtraction says " + wrong + " (negative: claims MAX_VALUE < -1)");
        System.out.println("Integer.compare says " + right + " (positive: correct)");


        // ============================================
        // SECTION 6: THE CONSISTENCY RULE
        // compareTo should agree with equals(): if compareTo returns 0, equals
        // should be true. Sorted collections (TreeSet, TreeMap) rely on
        // compare, not equals, as seen in _5_LinkedHashSetAndTreeSet.
        // ============================================


        // ============================================
        // SECTION 7: Comparable vs Comparator
        // Comparable  - one natural order, built into the class, compareTo(other)
        // Comparator  - any number of external orders, compare(a, b)
        // ============================================
    }
}
