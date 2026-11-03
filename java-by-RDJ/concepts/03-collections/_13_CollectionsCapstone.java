// Tags: #Java #Collections #CollectionsCapstone | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.*;

public class _13_CollectionsCapstone {

    // PART 2 building block: an LRU cache = a LinkedHashMap in access order
    // that evicts its eldest (least recently used) entry when it grows too big.
    static class LruCache<K, V> extends LinkedHashMap<K, V> {
        private final int capacity;

        LruCache(int capacity) {
            super(16, 0.75f, true);          // true = access order
            this.capacity = capacity;
        }

        @Override
        protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
            return size() > capacity;
        }
    }

    // PART 3 building block
    record Player(String name, int score, int level) {
    }

    public static void main(String[] args) {

        // ============================================
        // PART 1: WORD FREQUENCY COUNTER
        // Map (counting) -> List of entries -> Comparator chain (ranking)
        // ============================================

        String text = "the quick brown fox jumps over the lazy dog the fox";
        Map<String, Integer> freq = new HashMap<>();
        for (String word : text.split("\\s+")) {
            freq.merge(word, 1, Integer::sum);
        }

        List<Map.Entry<String, Integer>> entries = new ArrayList<>(freq.entrySet());
        Comparator<Map.Entry<String, Integer>> byCountThenWord =
                Map.Entry.<String, Integer>comparingByValue().reversed()
                        .thenComparing(Map.Entry.comparingByKey());
        entries.sort(byCountThenWord);

        System.out.println("Top 3 words:");
        for (int i = 0; i < 3; i++) {
            Map.Entry<String, Integer> e = entries.get(i);
            System.out.println("  " + (i + 1) + ". " + e.getKey() + " x" + e.getValue());
        }
        // The tie between "fox" and the 1-count words is broken alphabetically.


        // ============================================
        // PART 2: LRU CACHE (capacity 3)
        // ============================================

        LruCache<String, String> cache = new LruCache<>(3);
        cache.put("a", "1");
        cache.put("b", "2");
        cache.put("c", "3");
        cache.get("a");                 // "a" becomes the most recently used
        cache.put("d", "4");            // over capacity -> evicts the least recently used: "b"
        System.out.println("Cache keys (oldest first): " + cache.keySet());
        System.out.println("Contains b? " + cache.containsKey("b"));


        // ============================================
        // PART 3: LEADERBOARD - Comparator chain on records
        // Highest score first; ties go to the higher level; then name A-Z.
        // ============================================

        List<Player> players = new ArrayList<>(List.of(
                new Player("Kai", 900, 12),
                new Player("Lea", 1200, 9),
                new Player("Omar", 900, 15),
                new Player("Ana", 900, 15)));

        players.sort(Comparator.comparingInt(Player::score).reversed()
                .thenComparing(Comparator.comparingInt(Player::level).reversed())
                .thenComparing(Player::name));

        System.out.println("Leaderboard:");
        int rank = 1;
        for (Player p : players) {
            System.out.println("  #" + rank++ + " " + p.name() + " - " + p.score() + " pts, level " + p.level());
        }


        // ============================================
        // PART 4: WHICH COLLECTION DID EACH PART USE, AND WHY?
        // HashMap          - fast counting by key
        // ArrayList        - needs sorting by index, so a List
        // LinkedHashMap    - access order gives LRU eviction almost for free
        // Comparator chain - ranking by several rules, without editing the class
        // ============================================
    }
}
