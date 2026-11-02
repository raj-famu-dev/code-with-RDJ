// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.List;

public class _3_BoundedTypes {

    // ============================================
    // SECTION 1: THE PROBLEM
    // With a plain <T> you know NOTHING about T except that it is an Object.
    // So you cannot compare two Ts:
    //     static <T> T max(T a, T b) { return a > b ? a : b; }     // COMPILE ERROR: > needs numbers
    //     static <T> T max(T a, T b) { return a.compareTo(b) ... } // COMPILE ERROR: Object has no compareTo
    // ============================================

    // ============================================
    // SECTION 2: AN UPPER BOUND
    // <T extends Comparable<T>> says: "T must be a type that can compare itself to
    // another T". Now compareTo exists, and the compiler guarantees it.
    // ("extends" here means extends OR implements.)
    // ============================================

    static <T extends Comparable<T>> T max(T a, T b) {
        return a.compareTo(b) >= 0 ? a : b;
    }

    // Largest element of a list
    static <T extends Comparable<T>> T maxOf(List<T> items) {
        if (items.isEmpty()) {
            throw new IllegalArgumentException("list is empty");
        }
        T best = items.get(0);
        for (T item : items) {
            if (item.compareTo(best) > 0) {
                best = item;
            }
        }
        return best;
    }

    // How many items are strictly greater than a given one
    static <T extends Comparable<T>> int countGreaterThan(List<T> items, T limit) {
        int count = 0;
        for (T item : items) {
            if (item.compareTo(limit) > 0) {
                count++;
            }
        }
        return count;
    }

    // ============================================
    // SECTION 3: BOUNDING TO A CLASS - NUMBERS ONLY
    // Number is the parent of Integer, Double, Long...
    // It provides doubleValue(), so we can add anything numeric.
    // ============================================

    static <T extends Number> double sum(List<T> numbers) {
        double total = 0;
        for (T n : numbers) {
            total += n.doubleValue();
        }
        return total;
    }

    // ============================================
    // SECTION 4: A BOUNDED GENERIC CLASS
    // A "sorted holder" that keeps the biggest value seen so far.
    // ============================================

    static class MaxTracker<T extends Comparable<T>> {
        private T best;

        void offer(T candidate) {
            if (best == null || candidate.compareTo(best) > 0) {
                best = candidate;
            }
        }

        T best() {
            return best;
        }
    }

    // ============================================
    // SECTION 5: MULTIPLE BOUNDS
    // <T extends A & B & C>: if one is a class it must come FIRST; the rest are interfaces.
    // ============================================

    interface Named {
        String name();
    }

    record Employee(String name, int salary) implements Named, Comparable<Employee> {
        @Override
        public int compareTo(Employee other) {
            return Integer.compare(salary, other.salary);
        }
    }

    static <T extends Named & Comparable<T>> String nameOfBest(List<T> items) {
        T best = items.get(0);
        for (T item : items) {
            if (item.compareTo(best) > 0) {
                best = item;
            }
        }
        return best.name();                               // name() comes from Named, compareTo from Comparable
    }

    public static void main(String[] args) {

        System.out.println("max(3, 9)           = " + max(3, 9));
        System.out.println("max(\"pear\", \"apple\") = " + max("pear", "apple"));
        System.out.println("max(2.5, 1.5)      = " + max(2.5, 1.5));
        // max(new Object(), new Object());               // COMPILE ERROR: Object is not Comparable<Object>
        // max(1, "a");                                   // COMPILE ERROR: T cannot be both Integer and String

        List<Integer> scores = new ArrayList<>(List.of(55, 91, 78, 91, 12));
        System.out.println("maxOf(scores)       = " + maxOf(scores));
        System.out.println("countGreaterThan(70)= " + countGreaterThan(scores, 70));

        System.out.println("sum of Integers     = " + sum(List.of(1, 2, 3)));
        System.out.println("sum of Doubles      = " + sum(List.of(1.5, 2.5)));
        // sum(List.of("a", "b"));                        // COMPILE ERROR: String is not a Number

        MaxTracker<String> tracker = new MaxTracker<>();
        for (String word : List.of("kiwi", "fig", "plum", "banana")) {
            tracker.offer(word);
        }
        System.out.println("MaxTracker<String>  = " + tracker.best() + " (alphabetically last)");

        List<Employee> staff = List.of(new Employee("Ada", 120), new Employee("Linus", 150), new Employee("Grace", 90));
        System.out.println("highest paid        = " + nameOfBest(staff));

        // ============================================
        // SECTION 6: RULES TO REMEMBER
        // 1) <T extends X> = T is X or any subtype of X (class OR interface).
        // 2) A bound lets you CALL X's methods on a T.
        // 3) The bound is checked at compile time: wrong types never get in.
        // 4) <T extends Comparable<T>> is the standard pattern for "can be ordered".
        //    (Real library code often writes Comparable<? super T>: see _4_Wildcards.)
        // ============================================
    }
}
