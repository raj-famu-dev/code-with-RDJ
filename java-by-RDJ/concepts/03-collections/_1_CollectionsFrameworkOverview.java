// Tags: #Java #Collections #CollectionsFrameworkOverview | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.*;

public class _1_CollectionsFrameworkOverview {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THE HIERARCHY IN ONE PICTURE
        // Iterable
        //   -> Collection
        //        -> List   (ordered, duplicates allowed, index access)
        //        -> Set    (no duplicates)
        //        -> Queue  (processing order, usually FIFO)
        //             -> Deque (queue + stack at both ends)
        // Map  (key -> value pairs)  <-- a SEPARATE tree, NOT under Collection
        // Interfaces say WHAT you can do; classes (ArrayList, HashSet,
        // ArrayDeque, HashMap...) decide HOW it is stored and how fast it is.
        // ============================================

        Collection<String> asCollection = new ArrayList<>();
        Iterable<String> asIterable = asCollection;   // every Collection is Iterable
        System.out.println("A List is a Collection: " + (new ArrayList<String>() instanceof Collection));
        System.out.println("A Set is a Collection:  " + (new HashSet<String>() instanceof Collection));
        System.out.println("A Queue is a Collection: " + (new ArrayDeque<String>() instanceof Collection));


        // ============================================
        // SECTION 2: WHY MAP IS NOT A COLLECTION
        // Collection<E> is built around add(E) / remove(E) of ONE element.
        // A Map stores PAIRS: put(K, V). There is no sensible single-element add().
        // Map<K,V> therefore has its own interface, but it hands you
        // Collection VIEWS: keySet() (a Set), values() (a Collection),
        // entrySet() (a Set of Map.Entry).
        // ============================================

        Map<String, Integer> ages = new HashMap<>();
        ages.put("Ana", 20);
        // Collection<?> c = ages;      // COMPILE ERROR - Map is not a Collection
        Set<String> keys = ages.keySet();
        System.out.println("Keys view: " + keys + ", values view: " + ages.values());


        // ============================================
        // SECTION 3: PROGRAM TO THE INTERFACE
        // Declare the variable with the interface type, pick the class at 'new'.
        // Swapping implementations later is a one-word change.
        // ============================================

        List<String> names = new ArrayList<>();   // could become LinkedList without touching later code
        names.add("Zed");
        names.add("Amy");
        names.add("Zed");
        System.out.println("List keeps order + duplicates: " + names);


        // ============================================
        // SECTION 4: THE FOUR SHAPES SIDE BY SIDE
        // Same input, four different behaviours.
        // ============================================

        Set<String> set = new TreeSet<>(names);            // unique, here sorted
        Queue<String> queue = new ArrayDeque<>(names);     // FIFO
        System.out.println("Set (unique):    " + set);
        System.out.println("Queue poll():    " + queue.poll() + " (first in, first out)");

        Map<String, Integer> counts = new TreeMap<>();
        for (String n : names) {
            counts.merge(n, 1, Integer::sum);              // key -> how many times
        }
        System.out.println("Map (key->count): " + counts);


        // ============================================
        // SECTION 5: COMMON Collection METHODS
        // These work on List, Set and Queue alike because they live on Collection.
        // ============================================

        Collection<String> c = new ArrayList<>(names);
        System.out.println("size=" + c.size() + " contains(Amy)=" + c.contains("Amy") + " isEmpty=" + c.isEmpty());
        c.remove("Zed");                 // removes only the FIRST matching element in a List
        System.out.println("After remove(\"Zed\"): " + c);
        for (String s : asIterable) {    // anything Iterable works in for-each
            System.out.println("never printed, list is empty");
        }


        // ============================================
        // SECTION 6: PICKING A TYPE (QUICK GUIDE)
        // Need order + index access?       -> List
        // Need uniqueness?                 -> Set
        // Need to process items in turn?   -> Queue / Deque
        // Need lookup by a key?            -> Map
        // Details of each class come in the next files.
        // ============================================

        // Set<String> s2 = new ArrayList<>();   // COMPILE ERROR - ArrayList is a List, not a Set
        // Collection<String> c2 = new HashMap<>();   // COMPILE ERROR - same reason as Section 2
    }
}
