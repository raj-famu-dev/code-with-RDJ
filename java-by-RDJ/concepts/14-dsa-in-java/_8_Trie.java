// Tags: #Java #DSA #DataStructures #Trie | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.HashSet;
import java.util.Random;
import java.util.Set;

/**
 * TRIE (prefix tree). One node per character; a path from the root spells a word. Used for autocomplete, spell check,
 * and "does any word start with ...?" questions.
 * Nodes use a fixed array of 26 children (lowercase a-z only), so no java.util collections inside the structure.
 * java.util.HashSet is only the oracle in main().
 *
 * Big-O (L = length of the word or prefix, n = number of words, A = alphabet size = 26):
 *   insert, contains, startsWith, remove    O(L)   (independent of how many words are stored!)
 *   words with a given prefix               O(L + size of the output subtree)
 *   memory                                  O(total characters * A) with array children (wasteful), less with a map per node
 * Versus a HashSet of words: contains is O(L) for both (hashing a string is O(L)), but a hash set cannot answer
 * "which words start with 'ca'?" without scanning every word, and a trie can.
 */
public class _8_Trie {

    static class Trie {
        private static class Node {
            final Node[] children = new Node[26];
            boolean isWord;                                        // a node can be inside a longer word AND end a shorter one
            int wordsBelow;                                        // how many stored words pass through this node (for counts and safe removal)
        }

        private final Node root = new Node();
        private int size;

        int size() {
            return size;
        }

        boolean insert(String word) {
            validate(word);
            if (contains(word)) return false;                      // already present: nothing to change (keeps the counters exact)
            Node current = root;
            current.wordsBelow++;
            for (int i = 0; i < word.length(); i++) {
                int index = word.charAt(i) - 'a';
                if (current.children[index] == null) current.children[index] = new Node();
                current = current.children[index];
                current.wordsBelow++;
            }
            current.isWord = true;
            size++;
            return true;
        }

        boolean contains(String word) {
            validate(word);
            Node node = find(word);
            return node != null && node.isWord;                    // "car" exists as a PATH inside "card" but is not a WORD unless marked
        }

        boolean startsWith(String prefix) {
            validate(prefix);
            return find(prefix) != null;
        }

        int countWithPrefix(String prefix) {
            validate(prefix);
            Node node = find(prefix);
            return node == null ? 0 : node.wordsBelow;
        }

        // Remove a word. Nodes that no other word uses are unlinked so memory is released.
        boolean remove(String word) {
            validate(word);
            if (!contains(word)) return false;
            Node current = root;
            current.wordsBelow--;
            for (int i = 0; i < word.length(); i++) {
                int index = word.charAt(i) - 'a';
                Node child = current.children[index];
                child.wordsBelow--;
                if (child.wordsBelow == 0) {                       // nothing else passes through here: cut the whole branch
                    current.children[index] = null;
                    size--;
                    return true;
                }
                current = child;
            }
            current.isWord = false;                                // other words continue below: keep the nodes, drop the word mark
            size--;
            return true;
        }

        // Autocomplete: every stored word that starts with prefix, in alphabetical order (children are visited a..z)
        String[] wordsWithPrefix(String prefix) {
            validate(prefix);
            Node start = find(prefix);
            if (start == null) return new String[0];
            String[] results = new String[start.wordsBelow];
            int[] count = {0};
            collect(start, new StringBuilder(prefix), results, count);
            return results;
        }

        private void collect(Node node, StringBuilder path, String[] results, int[] count) {
            if (node.isWord) results[count[0]++] = path.toString();
            for (int c = 0; c < 26; c++) {
                if (node.children[c] != null) {
                    path.append((char) ('a' + c));
                    collect(node.children[c], path, results, count);
                    path.deleteCharAt(path.length() - 1);          // backtrack
                }
            }
        }

        // The longest stored word that is a prefix of the text (e.g. routing a path or finding the longest match)
        String longestPrefixOf(String text) {
            validate(text);
            Node current = root;
            int best = -1;
            for (int i = 0; i < text.length(); i++) {
                current = current.children[text.charAt(i) - 'a'];
                if (current == null) break;
                if (current.isWord) best = i + 1;
            }
            return best < 0 ? "" : text.substring(0, best);
        }

        private Node find(String s) {
            Node current = root;
            for (int i = 0; i < s.length(); i++) {
                current = current.children[s.charAt(i) - 'a'];
                if (current == null) return null;
            }
            return current;
        }

        private void validate(String s) {
            if (s == null) throw new IllegalArgumentException("null");
            for (int i = 0; i < s.length(); i++) {
                char c = s.charAt(i);
                if (c < 'a' || c > 'z') throw new IllegalArgumentException("only a-z supported, got '" + c + "' in \"" + s + "\"");
            }
        }
    }

    static String show(String[] words) {
        return words.length == 0 ? "(none)" : String.join(", ", words);
    }

    public static void main(String[] args) {

        Trie trie = new Trie();
        for (String w : new String[]{"car", "card", "care", "careful", "cat", "dog", "dot"}) trie.insert(w);
        System.out.println("size = " + trie.size());
        System.out.println("contains(car) = " + trie.contains("car") + ", contains(ca) = " + trie.contains("ca")
                + " (a PATH, not a word), startsWith(ca) = " + trie.startsWith("ca"));
        System.out.println("insert(car) again returns " + trie.insert("car") + ", size still " + trie.size());
        System.out.println("autocomplete \"car\": " + show(trie.wordsWithPrefix("car")));
        System.out.println("autocomplete \"ca\":  " + show(trie.wordsWithPrefix("ca")));
        System.out.println("autocomplete \"do\":  " + show(trie.wordsWithPrefix("do")));
        System.out.println("autocomplete \"x\":   " + show(trie.wordsWithPrefix("x")));
        System.out.println("countWithPrefix(\"car\") = " + trie.countWithPrefix("car") + ", countWithPrefix(\"d\") = " + trie.countWithPrefix("d"));
        System.out.println("longestPrefixOf(\"carefully\") = \"" + trie.longestPrefixOf("carefully") + "\"");

        // ---------- removal: leaf, word inside a longer word, and a branch no one else uses ----------
        trie.remove("careful");
        System.out.println("remove careful:  \"care\" still a word = " + trie.contains("care") + ", careful = " + trie.contains("careful"));
        trie.remove("car");
        System.out.println("remove car:      \"card\" and \"care\" survive = " + (trie.contains("card") && trie.contains("care"))
                + ", car = " + trie.contains("car") + ", startsWith(car) = " + trie.startsWith("car"));
        trie.remove("dog");
        trie.remove("dot");
        System.out.println("remove dog, dot: startsWith(d) = " + trie.startsWith("d") + "  (the whole branch was released)");
        System.out.println("remove(zebra) (absent) returns " + trie.remove("zebra") + ", size = " + trie.size());

        try {
            trie.insert("Hello");
        } catch (IllegalArgumentException e) {
            System.out.println("IllegalArgumentException: " + e.getMessage());
        }

        // ---------- ORACLE TEST: random words over a tiny alphabet so prefixes collide a lot ----------
        Random random = new Random(1234);
        Trie ours = new Trie();
        Set<String> oracle = new HashSet<>();
        boolean ok = true;
        for (int step = 0; step < 30_000; step++) {
            StringBuilder sb = new StringBuilder();
            int length = 1 + random.nextInt(5);
            for (int i = 0; i < length; i++) sb.append((char) ('a' + random.nextInt(3)));   // only a, b, c
            String word = sb.toString();
            switch (random.nextInt(3)) {
                case 0 -> ok &= ours.insert(word) == oracle.add(word);
                case 1 -> ok &= ours.remove(word) == oracle.remove(word);
                default -> ok &= ours.contains(word) == oracle.contains(word);
            }
            ok &= ours.size() == oracle.size();
        }
        // the prefix counts must agree with a brute-force scan of the oracle
        for (String prefix : new String[]{"a", "b", "ab", "abc", "ca", "cc", "bba"}) {
            int expected = 0;
            for (String w : oracle) if (w.startsWith(prefix)) expected++;
            ok &= ours.countWithPrefix(prefix) == expected;
            ok &= ours.wordsWithPrefix(prefix).length == expected;
        }
        System.out.println("oracle test: 30000 random operations match java.util.HashSet, prefix counts match a brute-force scan: " + ok
                + " (final size " + ours.size() + ")");

        // ============================================
        // THINGS TO BREAK ON PURPOSE
        // 1) In contains(): return node != null (forget isWord). Now contains("ca") is true. Why is that a bug and not a feature?
        // 2) In remove(): only clear isWord and never cut branches. Everything still "works", so what has been lost?
        // 3) Allow uppercase by using 52 children, or switch the children to a Map. What is the memory-versus-speed trade-off?
        // ============================================
    }
}
