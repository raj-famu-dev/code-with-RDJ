// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.*;

public class _5_LinkedHashSetAndTreeSet {

    // Deliberately NOT Comparable - used to show what TreeSet demands
    static class Plain {
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THREE SETS, THREE ORDERING PROMISES
        // HashSet        - no order promised
        // LinkedHashSet  - remembers INSERTION order
        // TreeSet        - keeps elements SORTED
        // ============================================

        List<String> input = List.of("pear", "apple", "fig", "apple", "banana");

        System.out.println("LinkedHashSet: " + new LinkedHashSet<>(input));
        System.out.println("TreeSet:       " + new TreeSet<>(input));
        // Duplicates ("apple") are dropped by both.


        // ============================================
        // SECTION 2: LinkedHashSet = HashSet + a linked list through the entries
        // Same O(1) average speed, a little more memory, predictable iteration.
        // Re-adding an existing element does NOT move it.
        // ============================================

        Set<String> linked = new LinkedHashSet<>();
        linked.add("c");
        linked.add("a");
        linked.add("b");
        linked.add("c");          // ignored, stays in its first position
        System.out.println("Insertion order kept: " + linked);


        // ============================================
        // SECTION 3: TreeSet - A SORTED SET (O(log n) per operation)
        // Internally a balanced tree (a red-black tree in OpenJDK).
        // Because it is sorted, it offers navigation methods.
        // ============================================

        TreeSet<Integer> nums = new TreeSet<>(List.of(10, 20, 30, 40));
        System.out.println("first=" + nums.first() + ", last=" + nums.last());
        System.out.println("floor(25)   = " + nums.floor(25) + "   (greatest <= 25)");
        System.out.println("ceiling(25) = " + nums.ceiling(25) + "   (smallest >= 25)");
        System.out.println("lower(20)   = " + nums.lower(20) + "   (strictly less)");
        System.out.println("higher(20)  = " + nums.higher(20) + "   (strictly greater)");
        System.out.println("headSet(30) = " + nums.headSet(30) + "   (< 30)");
        System.out.println("tailSet(30) = " + nums.tailSet(30) + "   (>= 30)");
        System.out.println("descending  = " + nums.descendingSet());


        // ============================================
        // SECTION 4: WHAT TreeSet REQUIRES OF ITS ELEMENTS
        // Either the elements implement Comparable, or you hand the TreeSet a
        // Comparator. Otherwise it cannot sort.
        // ============================================

        try {
            new TreeSet<Plain>().add(new Plain());
        } catch (ClassCastException e) {
            System.out.println("Caught ClassCastException: Plain is not Comparable");
        }


        // ============================================
        // SECTION 5: TRAP - THE COMPARATOR DEFINES "DUPLICATE" FOR A TreeSet
        // A TreeSet does not call equals(). If compare() returns 0, the two
        // elements are treated as the SAME element and the second is dropped.
        // ============================================

        Set<String> byLength = new TreeSet<>(Comparator.comparingInt(String::length));
        byLength.add("pear");
        byLength.add("plum");     // same length as "pear" -> compare == 0 -> dropped
        byLength.add("fig");
        System.out.println("Set sorted by length: " + byLength + "  (plum silently lost)");
        // Fix: add a tie-breaker, e.g. Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder())


        // ============================================
        // SECTION 6: CHOOSING
        // Need just uniqueness, fastest?            -> HashSet
        // Need uniqueness + insertion order?        -> LinkedHashSet
        // Need sorted order / range queries?        -> TreeSet
        // ============================================
    }
}
