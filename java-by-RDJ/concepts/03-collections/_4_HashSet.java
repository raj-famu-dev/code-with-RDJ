// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.*;

public class _4_HashSet {

    // Correct: equals AND hashCode are based on the same fields
    static class Point {
        final int x, y;

        Point(int x, int y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof Point p)) return false;
            return x == p.x && y == p.y;
        }

        @Override
        public int hashCode() {
            return Objects.hash(x, y);
        }

        @Override
        public String toString() {
            return "(" + x + "," + y + ")";
        }
    }

    // Broken ON PURPOSE: equals() without hashCode()
    static class BrokenPoint {
        final int x, y;

        BrokenPoint(int x, int y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public boolean equals(Object o) {
            return o instanceof BrokenPoint p && x == p.x && y == p.y;
        }
        // hashCode() NOT overridden -> inherits Object's identity-based hash code
    }

    // A key whose hashCode depends on a MUTABLE field
    static class Student {
        int id;

        Student(int id) {
            this.id = id;
        }

        @Override
        public boolean equals(Object o) {
            return o instanceof Student s && id == s.id;
        }

        @Override
        public int hashCode() {
            return id;      // kept simple so this demo is predictable
        }
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: A SET STORES EACH VALUE AT MOST ONCE
        // add() returns false when the element was already present.
        // ============================================

        Set<String> names = new HashSet<>();
        System.out.println("add Ana:  " + names.add("Ana"));
        System.out.println("add Ana:  " + names.add("Ana"));
        System.out.println("size = " + names.size());
        // Do NOT depend on the printing order of a HashSet - it is not specified.


        // ============================================
        // SECTION 2: HOW IT DECIDES TWO ELEMENTS ARE "THE SAME"
        // Step 1: hashCode() picks a bucket.
        // Step 2: inside that bucket, equals() confirms a real match.
        // A HashSet is a HashMap underneath: your element is the KEY.
        // ============================================

        Set<Point> points = new HashSet<>();
        points.add(new Point(1, 2));
        points.add(new Point(1, 2));
        System.out.println("Correct Point, size = " + points.size() + "  (the duplicate was recognised)");
        System.out.println("contains new Point(1,2): " + points.contains(new Point(1, 2)));


        // ============================================
        // SECTION 3: TRAP - equals() WITHOUT hashCode()
        // Two "equal" objects land in different buckets, so equals() is never
        // even asked. Result is almost always a duplicate you did not want.
        // (Almost always, not guaranteed: identity hash codes are arbitrary.)
        // ============================================

        Set<BrokenPoint> broken = new HashSet<>();
        broken.add(new BrokenPoint(1, 2));
        broken.add(new BrokenPoint(1, 2));
        System.out.println("BrokenPoint size = " + broken.size() + "  (expected 1; almost always 2)");
        System.out.println("contains new BrokenPoint(1,2): " + broken.contains(new BrokenPoint(1, 2)));


        // ============================================
        // SECTION 4: TRAP - MUTATING AN ELEMENT AFTER ADDING IT
        // The element was filed under its OLD hash. After the change, lookups
        // search the NEW bucket, so the element is still inside but unfindable.
        // ============================================

        Set<Student> students = new HashSet<>();
        Student s = new Student(1);
        students.add(s);
        System.out.println("contains before mutation: " + students.contains(s));
        s.id = 2;
        System.out.println("contains after id 1 -> 2: " + students.contains(s));
        System.out.println("size is still " + students.size() + " - the element is stuck in the wrong bucket");
        // Rule: only use IMMUTABLE objects (or never-changed fields) as set elements / map keys.


        // ============================================
        // SECTION 5: SET OPERATIONS
        // ============================================

        Set<Integer> a = new HashSet<>(List.of(1, 2, 3, 4));
        Set<Integer> b = new HashSet<>(List.of(3, 4, 5));

        Set<Integer> union = new HashSet<>(a);
        union.addAll(b);
        Set<Integer> intersection = new HashSet<>(a);
        intersection.retainAll(b);
        Set<Integer> difference = new HashSet<>(a);
        difference.removeAll(b);

        System.out.println("union        = " + new TreeSet<>(union));
        System.out.println("intersection = " + new TreeSet<>(intersection));
        System.out.println("difference   = " + new TreeSet<>(difference));
        // (copied into TreeSet only to print in a stable order)


        // ============================================
        // SECTION 6: COMPLEXITY
        // add / contains / remove   O(1) on average (O(n) worst case with heavy collisions)
        // iteration                 O(capacity + size)
        // ============================================
    }
}
