// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.Random;
import java.util.TreeSet;

/**
 * BINARY SEARCH TREE (BST). Every node's left subtree holds smaller keys, its right subtree holds larger keys.
 * NO java.util collections inside the tree (java.util.TreeSet is only the oracle in main()).
 *
 * Big-O (h = height of the tree, n = nodes):
 *   insert, contains, remove, min, max     O(h)
 *   in-order / pre-order / post-order      O(n)
 *   BALANCED tree:   h = O(log n)  -> everything above is O(log n)
 *   DEGENERATE tree (keys inserted already sorted): h = n -> everything above is O(n), it is a linked list
 * This tree does NOT rebalance itself. AVL and red-black trees (inside TreeMap) add rotations to guarantee O(log n).
 */
public class _5_BinarySearchTree {

    static class Bst {
        private static class Node {
            int key;
            Node left;
            Node right;

            Node(int key) {
                this.key = key;
            }
        }

        private Node root;
        private int size;

        int size() {
            return size;
        }

        boolean contains(int key) {
            Node current = root;
            while (current != null) {
                if (key == current.key) return true;
                current = key < current.key ? current.left : current.right;   // discard half (if balanced) every step
            }
            return false;
        }

        boolean insert(int key) {
            if (root == null) {
                root = new Node(key);
                size++;
                return true;
            }
            Node current = root;
            while (true) {
                if (key == current.key) return false;              // duplicates are ignored (set semantics)
                if (key < current.key) {
                    if (current.left == null) {
                        current.left = new Node(key);
                        break;
                    }
                    current = current.left;
                } else {
                    if (current.right == null) {
                        current.right = new Node(key);
                        break;
                    }
                    current = current.right;
                }
            }
            size++;
            return true;
        }

        // REMOVE has three cases:
        //   1) leaf: just unlink it
        //   2) one child: replace the node with that child
        //   3) two children: replace the key with its IN-ORDER SUCCESSOR (smallest key of the right subtree), then
        //      remove that successor from the right subtree
        boolean remove(int key) {
            int before = size;
            root = remove(root, key);
            return size < before;
        }

        private Node remove(Node node, int key) {
            if (node == null) return null;                         // not found
            if (key < node.key) {
                node.left = remove(node.left, key);
            } else if (key > node.key) {
                node.right = remove(node.right, key);
            } else {
                if (node.left == null) {
                    size--;
                    return node.right;                             // cases 1 and 2a
                }
                if (node.right == null) {
                    size--;
                    return node.left;                              // case 2b
                }
                Node successor = node.right;                       // case 3
                while (successor.left != null) successor = successor.left;
                node.key = successor.key;                          // copy the successor's key up...
                node.right = remove(node.right, successor.key);    // ...and delete the original (this call does size--)
            }
            return node;
        }

        int min() {
            if (root == null) throw new java.util.NoSuchElementException("tree is empty");
            Node n = root;
            while (n.left != null) n = n.left;
            return n.key;
        }

        int max() {
            if (root == null) throw new java.util.NoSuchElementException("tree is empty");
            Node n = root;
            while (n.right != null) n = n.right;
            return n.key;
        }

        int height() {
            return height(root);
        }

        private int height(Node n) {
            return n == null ? 0 : 1 + Math.max(height(n.left), height(n.right));
        }

        // ---- traversals (they append to a StringBuilder to avoid using any collection) ----
        String inOrder() {                                         // left, node, right -> SORTED ascending
            StringBuilder sb = new StringBuilder();
            inOrder(root, sb);
            return sb.toString().trim();
        }

        private void inOrder(Node n, StringBuilder sb) {
            if (n == null) return;
            inOrder(n.left, sb);
            sb.append(n.key).append(' ');
            inOrder(n.right, sb);
        }

        String preOrder() {                                        // node, left, right -> the order to COPY a tree
            StringBuilder sb = new StringBuilder();
            preOrder(root, sb);
            return sb.toString().trim();
        }

        private void preOrder(Node n, StringBuilder sb) {
            if (n == null) return;
            sb.append(n.key).append(' ');
            preOrder(n.left, sb);
            preOrder(n.right, sb);
        }

        String postOrder() {                                       // left, right, node -> the order to DELETE a tree
            StringBuilder sb = new StringBuilder();
            postOrder(root, sb);
            return sb.toString().trim();
        }

        private void postOrder(Node n, StringBuilder sb) {
            if (n == null) return;
            postOrder(n.left, sb);
            postOrder(n.right, sb);
            sb.append(n.key).append(' ');
        }

        // Level order (breadth-first) needs a queue: we use a plain array as a mini queue so no java.util is involved
        String levelOrder() {
            if (root == null) return "";
            Node[] queue = new Node[size];
            int head = 0;
            int tail = 0;
            queue[tail++] = root;
            StringBuilder sb = new StringBuilder();
            while (head < tail) {
                Node n = queue[head++];
                sb.append(n.key).append(' ');
                if (n.left != null) queue[tail++] = n.left;
                if (n.right != null) queue[tail++] = n.right;
            }
            return sb.toString().trim();
        }

        // Is this really a BST? Pass down the allowed (low, high) range; every node must stay inside it.
        // (Checking only "left < node < right" for direct children is the classic WRONG answer.)
        boolean isValid() {
            return isValid(root, Long.MIN_VALUE, Long.MAX_VALUE);
        }

        private boolean isValid(Node n, long low, long high) {
            if (n == null) return true;
            if (n.key <= low || n.key >= high) return false;
            return isValid(n.left, low, n.key) && isValid(n.right, n.key, high);
        }
    }

    public static void main(String[] args) {

        // ---------- the classic textbook tree ----------
        Bst tree = new Bst();
        for (int key : new int[]{50, 30, 70, 20, 40, 60, 80, 35}) tree.insert(key);
        System.out.println("size = " + tree.size() + ", height = " + tree.height() + ", min = " + tree.min() + ", max = " + tree.max());
        System.out.println("in-order    (sorted):    " + tree.inOrder());
        System.out.println("pre-order   (node first): " + tree.preOrder());
        System.out.println("post-order  (node last):  " + tree.postOrder());
        System.out.println("level-order (by depth):   " + tree.levelOrder());
        System.out.println("contains(60) = " + tree.contains(60) + ", contains(65) = " + tree.contains(65));
        System.out.println("insert(50) again returns " + tree.insert(50) + " (duplicate ignored), size " + tree.size());

        // ---------- the three removal cases ----------
        tree.remove(20);                                           // leaf
        System.out.println("remove leaf 20:        " + tree.levelOrder());
        tree.remove(30);                                           // one child (40, which has child 35)
        System.out.println("remove one-child 30:   " + tree.levelOrder());
        tree.remove(50);                                           // two children: the root, successor is 60
        System.out.println("remove two-child 50:   " + tree.levelOrder() + "   (60 replaced it)");
        System.out.println("still valid BST: " + tree.isValid() + ", in-order still sorted: " + tree.inOrder());
        System.out.println("remove(999) (absent) returns " + tree.remove(999));

        // ---------- balanced vs degenerate: the whole reason balancing exists ----------
        Bst sortedInsert = new Bst();
        for (int i = 1; i <= 1000; i++) sortedInsert.insert(i);    // already sorted: every node goes to the right
        Bst shuffled = new Bst();
        int[] keys = new int[1000];
        for (int i = 0; i < keys.length; i++) keys[i] = i + 1;
        Random random = new Random(5);
        for (int i = keys.length - 1; i > 0; i--) {                // Fisher-Yates shuffle with a fixed seed
            int j = random.nextInt(i + 1);
            int tmp = keys[i];
            keys[i] = keys[j];
            keys[j] = tmp;
        }
        for (int key : keys) shuffled.insert(key);
        System.out.println("1000 keys inserted SORTED:   height = " + sortedInsert.height() + "   (a linked list in disguise: O(n))");
        System.out.println("1000 keys inserted SHUFFLED: height = " + shuffled.height() + "   (a perfect tree would be 10; random insertion order is only ROUGHLY balanced, here about 2.4x that)");

        // ---------- ORACLE TEST vs java.util.TreeSet ----------
        Random r = new Random(31337);
        Bst ours = new Bst();
        TreeSet<Integer> oracle = new TreeSet<>();
        boolean ok = true;
        for (int step = 0; step < 30_000; step++) {
            int key = r.nextInt(500);
            switch (r.nextInt(3)) {
                case 0 -> ok &= ours.insert(key) == oracle.add(key);
                case 1 -> ok &= ours.remove(key) == oracle.remove(key);
                default -> ok &= ours.contains(key) == oracle.contains(key);
            }
            ok &= ours.size() == oracle.size();
        }
        StringBuilder expected = new StringBuilder();
        for (int v : oracle) expected.append(v).append(' ');
        ok &= ours.inOrder().equals(expected.toString().trim());
        ok &= ours.isValid();
        System.out.println("oracle test: 30000 random operations match java.util.TreeSet, tree still valid: " + ok + " (final size " + ours.size() + ")");

        // ============================================
        // THINGS TO BREAK ON PURPOSE
        // 1) Replace isValid with a check that only compares each node to its direct children, then build a tree where
        //    that passes but the tree is invalid (hint: a node in the left subtree larger than the root).
        // 2) Remove the successor copy in case 3 and just return node.left. What data do you lose?
        // 3) Insert the keys 1..50000 sorted and call height() or any recursive method: watch StackOverflowError.
        // ============================================
    }
}
