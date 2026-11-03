// Tags: #Java #Collections #LinkedHashMapTree | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.*;

public class _8_LinkedHashMapAndTreeMap {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THREE MAPS, THREE ORDERING PROMISES
        // HashMap        - no order promised
        // LinkedHashMap  - INSERTION order (or ACCESS order, see Section 3)
        // TreeMap        - keys kept SORTED
        // ============================================

        Map<String, Integer> linked = new LinkedHashMap<>();
        linked.put("zebra", 1);
        linked.put("apple", 2);
        linked.put("mango", 3);
        System.out.println("LinkedHashMap: " + linked);
        System.out.println("TreeMap:       " + new TreeMap<>(linked));


        // ============================================
        // SECTION 2: re-putting AN EXISTING KEY DOES NOT MOVE IT
        // ============================================

        linked.put("zebra", 100);
        System.out.println("After updating zebra: " + linked);


        // ============================================
        // SECTION 3: ACCESS ORDER - THE BASIS OF AN LRU CACHE
        // The third constructor argument 'true' switches to access order:
        // every get() or put() moves that entry to the END.
        // So the FIRST entry is always the least recently used.
        // ============================================

        LinkedHashMap<String, Integer> access = new LinkedHashMap<>(16, 0.75f, true);
        access.put("a", 1);
        access.put("b", 2);
        access.put("c", 3);
        access.get("a");                       // "a" is now the most recently used
        System.out.println("Access order: " + access.keySet() + "  (least recent first)");
        // The full LRU cache is built in _13_CollectionsCapstone.


        // ============================================
        // SECTION 4: TreeMap - SORTED KEYS, O(log n) OPERATIONS
        // ============================================

        TreeMap<Integer, String> grades = new TreeMap<>();
        grades.put(90, "A");
        grades.put(80, "B");
        grades.put(70, "C");
        grades.put(60, "D");

        System.out.println("firstKey=" + grades.firstKey() + ", lastKey=" + grades.lastKey());
        System.out.println("headMap(80) = " + grades.headMap(80) + "   (keys < 80)");
        System.out.println("tailMap(80) = " + grades.tailMap(80) + "   (keys >= 80)");
        System.out.println("descending  = " + grades.descendingMap());


        // ============================================
        // SECTION 5: THE CLASSIC USE - RANGE LOOKUP WITH floorEntry
        // "Which grade band does a score of 85 fall into?"
        // floorEntry(k) = the entry with the greatest key <= k.
        // ============================================

        int score = 85;
        Map.Entry<Integer, String> band = grades.floorEntry(score);
        System.out.println("Score " + score + " -> grade " + band.getValue()
                + " (band starts at " + band.getKey() + ")");
        System.out.println("ceilingEntry(85) = " + grades.ceilingEntry(score));


        // ============================================
        // SECTION 6: TRAP - TreeMap AND NULL KEYS
        // HashMap accepts one null key. A TreeMap using natural ordering cannot
        // compare null, so it throws.
        // ============================================

        try {
            grades.put(null, "?");
        } catch (NullPointerException e) {
            System.out.println("Caught NullPointerException: TreeMap rejects a null key");
        }


        // ============================================
        // SECTION 7: A CUSTOM ORDER
        // ============================================

        TreeMap<String, Integer> reversed = new TreeMap<>(Comparator.reverseOrder());
        reversed.put("b", 2);
        reversed.put("a", 1);
        reversed.put("c", 3);
        System.out.println("Reverse-sorted keys: " + reversed);


        // ============================================
        // SECTION 8: CHOOSING
        // Fastest lookup, order irrelevant?    -> HashMap
        // Need insertion/access order or LRU?  -> LinkedHashMap
        // Need sorted keys / range queries?    -> TreeMap
        // ============================================
    }
}
