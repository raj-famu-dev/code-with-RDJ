// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

/**
 * HASH MAP WITH CHAINING. A table (array) of "buckets"; each bucket is a linked chain of entries whose keys landed there.
 * NO java.util collections inside the map (java.util.HashMap is only the oracle in main()).
 * (03-collections/_7_HashMapInternals has a minimal version. This one adds resizing, removal and an oracle test.)
 *
 * How it works:
 *   1) hash = key.hashCode(), spread so high bits matter:  h ^ (h >>> 16)
 *   2) bucket index = hash & (table.length - 1)   (table length is always a power of two, so & works like %)
 *   3) walk that bucket's chain comparing keys with equals(); update, or add a new node at the front
 *   4) when size > loadFactor * capacity (0.75), DOUBLE the table and re-insert every entry ("rehash")
 *
 * Big-O (n = entries, capacity grows with n so chains stay short):
 *   get, put, remove, containsKey   O(1) on average (needs a decent hashCode and the table kept below load factor 0.75)
 *                                   O(n) in the WORST case: if every key lands in one bucket it is just a linked list
 *   resize                          O(n), but rare: put() is amortized O(1)
 *   iteration                       O(capacity + n)
 */
public class _4_HashMapWithChaining {

    static class ChainedHashMap<K, V> {
        private static class Node<K, V> {
            final K key;
            final int hash;
            V value;
            Node<K, V> next;

            Node(K key, int hash, V value, Node<K, V> next) {
                this.key = key;
                this.hash = hash;
                this.value = value;
                this.next = next;
            }
        }

        private static final double LOAD_FACTOR = 0.75;

        private Node<K, V>[] table = newTable(8);
        private int size;
        int resizes;
        int longestChainEver;

        @SuppressWarnings({"unchecked", "rawtypes"})
        private static <K, V> Node<K, V>[] newTable(int capacity) {
            return (Node<K, V>[]) new Node[capacity];              // generic array creation needs this cast (see 06 _5)
        }

        int size() {
            return size;
        }

        int capacity() {
            return table.length;
        }

        private static int spread(Object key) {
            int h = key == null ? 0 : key.hashCode();
            return h ^ (h >>> 16);                                 // mix high bits into the low bits we actually use
        }

        V get(K key) {
            int hash = spread(key);
            for (Node<K, V> n = table[hash & (table.length - 1)]; n != null; n = n.next) {
                if (n.hash == hash && (n.key == key || (key != null && key.equals(n.key)))) {
                    return n.value;
                }
            }
            return null;
        }

        boolean containsKey(K key) {
            int hash = spread(key);
            for (Node<K, V> n = table[hash & (table.length - 1)]; n != null; n = n.next) {
                if (n.hash == hash && (n.key == key || (key != null && key.equals(n.key)))) return true;
            }
            return false;
        }

        V put(K key, V value) {
            int hash = spread(key);
            int index = hash & (table.length - 1);
            int chainLength = 0;
            for (Node<K, V> n = table[index]; n != null; n = n.next) {
                chainLength++;
                if (n.hash == hash && (n.key == key || (key != null && key.equals(n.key)))) {
                    V old = n.value;                               // key exists: REPLACE the value, size unchanged
                    n.value = value;
                    return old;
                }
            }
            table[index] = new Node<>(key, hash, value, table[index]);   // add at the FRONT of the chain: O(1)
            chainLength++;
            longestChainEver = Math.max(longestChainEver, chainLength);
            size++;
            if (size > LOAD_FACTOR * table.length) {
                resize();
            }
            return null;
        }

        V remove(K key) {
            int hash = spread(key);
            int index = hash & (table.length - 1);
            Node<K, V> previous = null;
            for (Node<K, V> n = table[index]; n != null; previous = n, n = n.next) {
                if (n.hash == hash && (n.key == key || (key != null && key.equals(n.key)))) {
                    if (previous == null) table[index] = n.next;   // removing the first node of the chain
                    else previous.next = n.next;                   // unlink from the middle or end
                    size--;
                    return n.value;
                }
            }
            return null;
        }

        private void resize() {
            Node<K, V>[] old = table;
            table = newTable(old.length * 2);
            for (Node<K, V> head : old) {
                for (Node<K, V> n = head; n != null; ) {
                    Node<K, V> next = n.next;                      // save before re-linking
                    int index = n.hash & (table.length - 1);       // the stored hash is reused: no need to call hashCode again
                    n.next = table[index];
                    table[index] = n;
                    n = next;
                }
            }
            resizes++;
        }

        // How full is the table, and how long are the chains? Useful to SEE collisions.
        String stats() {
            int used = 0;
            int longest = 0;
            for (Node<K, V> head : table) {
                if (head != null) {
                    used++;
                    int len = 0;
                    for (Node<K, V> n = head; n != null; n = n.next) len++;
                    longest = Math.max(longest, len);
                }
            }
            return "entries=" + size + ", buckets=" + table.length + ", buckets in use=" + used + ", longest chain=" + longest;
        }
    }

    // A key class with a TERRIBLE hashCode: every instance lands in the same bucket
    static final class BadKey {
        final int id;

        BadKey(int id) {
            this.id = id;
        }

        @Override
        public boolean equals(Object o) {
            return o instanceof BadKey b && b.id == id;
        }

        @Override
        public int hashCode() {
            return 42;                                             // legal, but useless
        }
    }

    // A key class that overrides equals but FORGETS hashCode (the classic bug)
    static final class ForgetfulKey {
        final String name;

        ForgetfulKey(String name) {
            this.name = name;
        }

        @Override
        public boolean equals(Object o) {
            return o instanceof ForgetfulKey k && k.name.equals(name);
        }
        // no hashCode() override: the default one is based on the object's identity
    }

    public static void main(String[] args) {

        // ---------- basics ----------
        ChainedHashMap<String, Integer> ages = new ChainedHashMap<>();
        ages.put("Ada", 36);
        ages.put("Linus", 55);
        ages.put("Grace", 85);
        System.out.println("get(Ada) = " + ages.get("Ada") + ", get(Zed) = " + ages.get("Zed") + ", size = " + ages.size());
        System.out.println("put(Ada, 37) returned the old value: " + ages.put("Ada", 37) + ", size still " + ages.size());
        System.out.println("remove(Linus) = " + ages.remove("Linus") + ", containsKey(Linus) = " + ages.containsKey("Linus"));
        ages.put(null, -1);
        System.out.println("a null key works here (like HashMap): " + ages.get(null));

        // ---------- growth ----------
        ChainedHashMap<Integer, Integer> growing = new ChainedHashMap<>();
        for (int i = 0; i < 1000; i++) growing.put(i, i * i);
        System.out.println("after 1000 puts: " + growing.stats() + ", resizes=" + growing.resizes);
        boolean allFound = true;
        for (int i = 0; i < 1000; i++) allFound &= growing.get(i) == i * i;
        System.out.println("all 1000 still found after rehashing: " + allFound);

        // ---------- good hash vs bad hash ----------
        ChainedHashMap<BadKey, Integer> bad = new ChainedHashMap<>();
        for (int i = 0; i < 500; i++) bad.put(new BadKey(i), i);
        System.out.println("500 keys with hashCode() == 42:   " + bad.stats() + "   <- one giant chain: a linked list");
        ChainedHashMap<Integer, Integer> good = new ChainedHashMap<>();
        for (int i = 0; i < 500; i++) good.put(i, i);
        System.out.println("500 keys with a proper hashCode: " + good.stats());

        // ---------- equals without hashCode ----------
        ChainedHashMap<ForgetfulKey, String> forgetful = new ChainedHashMap<>();
        forgetful.put(new ForgetfulKey("ada"), "found me");
        System.out.println("equals() overridden but not hashCode(): get(new ForgetfulKey(\"ada\")) = "
                + forgetful.get(new ForgetfulKey("ada")) + "   <- the equal key hashes elsewhere");

        // ---------- ORACLE TEST: 50,000 random operations vs java.util.HashMap ----------
        Random random = new Random(99);
        ChainedHashMap<Integer, Integer> ours = new ChainedHashMap<>();
        Map<Integer, Integer> oracle = new HashMap<>();
        boolean ok = true;
        for (int step = 0; step < 50_000; step++) {
            int key = random.nextInt(2_000);
            switch (random.nextInt(3)) {
                case 0 -> {
                    int value = random.nextInt();
                    Integer a = ours.put(key, value);
                    Integer b = oracle.put(key, value);
                    ok &= java.util.Objects.equals(a, b);
                }
                case 1 -> {
                    Integer a = ours.remove(key);
                    Integer b = oracle.remove(key);
                    ok &= java.util.Objects.equals(a, b);
                }
                default -> ok &= java.util.Objects.equals(ours.get(key), oracle.get(key));
            }
            ok &= ours.size() == oracle.size();
        }
        System.out.println("oracle test: 50000 random operations match java.util.HashMap: " + ok + " (final size " + ours.size() + ")");

        // ============================================
        // THINGS TO BREAK ON PURPOSE
        // 1) Change the index to hash % table.length (no bitmask) and give a negative hash. What happens?
        // 2) Never resize: with 100,000 keys watch the longest chain grow.
        // 3) In resize(): forget to save `next` before re-linking. The entries vanish. Why?
        // ============================================
    }
}
