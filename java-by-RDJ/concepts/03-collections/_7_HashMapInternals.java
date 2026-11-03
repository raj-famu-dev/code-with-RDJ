// Tags: #Java #Collections #HashMapInternals | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.*;

public class _7_HashMapInternals {

    // A deliberately simplified hash table with chaining, to make the idea visible.
    // The real java.util.HashMap is more sophisticated (see notes in Section 6).
    static class MiniMap {

        static class Node {
            final String key;
            int value;
            Node next;

            Node(String key, int value, Node next) {
                this.key = key;
                this.value = value;
                this.next = next;
            }
        }

        static final double LOAD_FACTOR = 0.75;
        Node[] table = new Node[4];         // the "buckets"
        int size = 0;

        int indexFor(String key) {
            return (key.hashCode() & 0x7fffffff) % table.length;
        }

        void put(String key, int value) {
            int idx = indexFor(key);
            for (Node n = table[idx]; n != null; n = n.next) {
                if (n.key.equals(key)) {         // same key already there: replace
                    n.value = value;
                    return;
                }
            }
            table[idx] = new Node(key, value, table[idx]);     // add to the front of the chain
            size++;
            if (size > table.length * LOAD_FACTOR) {
                resize();
            }
        }

        Integer get(String key) {
            for (Node n = table[indexFor(key)]; n != null; n = n.next) {
                if (n.key.equals(key)) return n.value;
            }
            return null;
        }

        void resize() {
            Node[] old = table;
            table = new Node[old.length * 2];
            for (Node head : old) {
                Node n = head;
                while (n != null) {
                    Node next = n.next;
                    int idx = indexFor(n.key);       // new table length => new bucket
                    n.next = table[idx];
                    table[idx] = n;
                    n = next;
                }
            }
        }

        void printBuckets() {
            for (int i = 0; i < table.length; i++) {
                StringBuilder sb = new StringBuilder("  bucket " + i + ": ");
                for (Node n = table[i]; n != null; n = n.next) {
                    sb.append(n.key).append(" -> ");
                }
                System.out.println(sb.append("end"));
            }
        }
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THE BIG IDEA
        // A hash map is an ARRAY of buckets.
        // key.hashCode() is turned into an array index, so the right bucket is
        // found in one step - no searching through every entry.
        // ============================================

        MiniMap map = new MiniMap();
        String[] keys = {"apple", "banana", "cherry", "date", "elderberry", "fig"};


        // ============================================
        // SECTION 2: WATCH IT GROW (LOAD FACTOR 0.75)
        // When size exceeds capacity * 0.75, the table doubles and EVERY entry
        // is re-placed (rehashed). That is why resizing costs O(n).
        // ============================================

        int value = 1;
        for (String k : keys) {
            map.put(k, value++);
            System.out.println("put " + k + " -> size=" + map.size + ", capacity=" + map.table.length);
        }
        map.printBuckets();
        System.out.println("get(date) = " + map.get("date") + ", get(grape) = " + map.get("grape"));


        // ============================================
        // SECTION 3: COLLISIONS ARE NORMAL
        // Different keys can land in the same bucket. Entries in one bucket are
        // chained together, and equals() decides which one you meant.
        // ============================================

        System.out.println("\"Aa\".hashCode() = " + "Aa".hashCode() + ", \"BB\".hashCode() = " + "BB".hashCode());
        Map<String, Integer> real = new HashMap<>();
        real.put("Aa", 1);
        real.put("BB", 2);
        System.out.println("Same hash code, still two separate keys: " + real.get("Aa") + " and " + real.get("BB"));
        // Equal hash codes do not mean equal objects - that is why equals() exists too.


        // ============================================
        // SECTION 4: WHY hashCode() QUALITY MATTERS
        // If every key had the same hash code, they would all pile into ONE
        // bucket and lookups would degrade from O(1) towards O(n).
        // ============================================


        // ============================================
        // SECTION 5: THE REAL HashMap (JAVA 8+, OpenJDK)
        // - default capacity 16, load factor 0.75, capacity is always a power of two
        // - it mixes the hash bits before choosing a bucket, to spread keys better
        // - when ONE bucket gets long (threshold 8, and the table is big enough),
        //   that bucket's chain is converted to a balanced tree: worst case O(log n)
        // These are implementation details, not guarantees from the specification.
        // ============================================


        // ============================================
        // SECTION 6: WHAT TO REMEMBER
        // put/get = hashCode -> bucket -> equals inside the bucket
        // Pre-size a HashMap if you know roughly how many entries it will hold:
        // new HashMap<>(expectedSize * 4 / 3 + 1) avoids repeated resizing.
        // ============================================
    }
}
