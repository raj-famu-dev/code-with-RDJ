// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.*;

public class _6_HashMap {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: put AND get
        // put() returns the PREVIOUS value for that key (or null if there was none).
        // get() returns null when the key is missing.
        // ============================================

        Map<String, Integer> stock = new HashMap<>();
        System.out.println("put apple=5 returned: " + stock.put("apple", 5));
        System.out.println("put apple=7 returned: " + stock.put("apple", 7));
        stock.put("pear", 3);
        System.out.println("get apple: " + stock.get("apple") + ", get kiwi: " + stock.get("kiwi"));


        // ============================================
        // SECTION 2: SAFER LOOKUPS AND UPDATES
        // ============================================

        System.out.println("getOrDefault kiwi: " + stock.getOrDefault("kiwi", 0));

        stock.putIfAbsent("pear", 99);       // pear already exists -> ignored
        stock.putIfAbsent("plum", 10);       // new key -> added
        System.out.println("containsKey plum: " + stock.containsKey("plum")
                + ", containsValue 10: " + stock.containsValue(10));

        stock.merge("apple", 1, Integer::sum);       // key exists: 7 + 1
        stock.merge("fig", 1, Integer::sum);         // key missing: stores 1
        System.out.println("After merge: " + new TreeMap<>(stock));
        // (copied into a TreeMap only so the printing order is stable)


        // ============================================
        // SECTION 3: COUNTING AND GROUPING - THE TWO MOST COMMON PATTERNS
        // ============================================

        String[] words = {"cat", "dog", "bird", "fish", "ant", "cow"};

        Map<Integer, List<String>> byLength = new TreeMap<>();
        for (String w : words) {
            byLength.computeIfAbsent(w.length(), k -> new ArrayList<>()).add(w);
        }
        System.out.println("Grouped by length: " + byLength);

        Map<Character, Integer> firstLetterCount = new TreeMap<>();
        for (String w : words) {
            firstLetterCount.merge(w.charAt(0), 1, Integer::sum);
        }
        System.out.println("Count by first letter: " + firstLetterCount);


        // ============================================
        // SECTION 4: ITERATING - USE entrySet() WHEN YOU NEED KEY AND VALUE
        // Calling get() inside a keySet() loop does a second lookup for no reason.
        // ============================================

        for (Map.Entry<String, Integer> e : new TreeMap<>(stock).entrySet()) {
            System.out.println("  " + e.getKey() + " -> " + e.getValue());
        }
        // stock.forEach((k, v) -> ...) is the shorter lambda form.


        // ============================================
        // SECTION 5: TRAP - AUTO-UNBOXING A MISSING KEY
        // get() returns Integer (an object) which may be null.
        // Assigning it to an int unboxes it, and unboxing null crashes.
        // ============================================

        try {
            int missing = stock.get("nope");
            System.out.println(missing);
        } catch (NullPointerException e) {
            System.out.println("Caught NullPointerException: unboxing null");
        }
        // Fix: getOrDefault("nope", 0), or check containsKey first.


        // ============================================
        // SECTION 6: NULLS, REMOVAL, AND VIEWS
        // HashMap allows ONE null key and many null values.
        // keySet(), values() and entrySet() are live VIEWS of the map.
        // ============================================

        Map<String, Integer> small = new HashMap<>();
        small.put(null, 1);
        small.put("a", null);
        System.out.println("null key works: " + small.get(null) + ", null value: " + small.get("a"));
        // Because null can mean "missing" OR "stored null", use containsKey to tell them apart.

        small.remove(null);
        System.out.println("After remove(null): size = " + small.size());


        // ============================================
        // SECTION 7: COMPLEXITY
        // put / get / remove / containsKey   O(1) on average
        // containsValue                      O(n)  (must scan every value)
        // Iteration order is NOT specified.
        // ============================================
    }
}
