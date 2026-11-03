// Tags: #Java #Collections #LinkedList | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.*;

public class _3_LinkedList {

    // A hand-made node, so we can SEE why LinkedList behaves the way it does
    static class Node {
        String value;
        Node next;

        Node(String value) {
            this.value = value;
        }
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT A LINKEDLIST IS
        // A chain of nodes. Each node holds a value and links to its neighbours.
        // Java's LinkedList is doubly linked (previous + next) and implements
        // BOTH List and Deque, so it has index methods AND first/last methods.
        // ============================================

        LinkedList<String> list = new LinkedList<>();
        list.add("b");
        list.addFirst("a");
        list.addLast("c");
        System.out.println("list = " + list);


        // ============================================
        // SECTION 2: WHY get(i) IS O(n)
        // Nodes are scattered in memory. There is no formula to jump to index i,
        // so you have to walk from one end, hop by hop.
        // ============================================

        Node head = new Node("a");
        head.next = new Node("b");
        head.next.next = new Node("c");

        Node current = head;
        int hops = 0;
        while (hops < 2) {
            current = current.next;
            hops++;
        }
        System.out.println("Reached index 2 after " + hops + " hops: " + current.value);
        System.out.println("list.get(2) walks the same way internally: " + list.get(2));
        // (OpenJDK starts from whichever end is closer - an implementation detail)


        // ============================================
        // SECTION 3: THE TWO ENDS ARE CHEAP (O(1))
        // Java keeps references to both the first and the last node.
        // ============================================

        list.addFirst("start");
        list.addLast("end");
        System.out.println("getFirst=" + list.getFirst() + ", getLast=" + list.getLast());
        list.removeFirst();
        list.removeLast();
        System.out.println("After removing both ends: " + list);


        // ============================================
        // SECTION 4: TRAP - "INSERTING IN THE MIDDLE IS O(1)" IS ONLY HALF TRUE
        // Re-linking the nodes is O(1), but FINDING the position is O(n).
        // So add(index, x) is O(n) overall.
        // ============================================

        list.add(1, "x");     // walks to index 1 first, then links the new node in
        System.out.println("After add(1, \"x\"): " + list);


        // ============================================
        // SECTION 5: WHERE IT GENUINELY WINS - REMOVING WHILE ALREADY POSITIONED
        // An Iterator already holds its place, so it.remove() needs no search.
        // ============================================

        Iterator<String> it = list.iterator();
        while (it.hasNext()) {
            if (it.next().equals("x")) {
                it.remove();
            }
        }
        System.out.println("After iterator removal: " + list);


        // ============================================
        // SECTION 6: SO WHEN SHOULD YOU USE IT?
        // Each element costs a whole node object (value + two links), so it uses
        // more memory and has poor cache locality than an array.
        // In practice ArrayList wins for lists, and ArrayDeque wins for
        // queues/stacks. Reach for LinkedList only when you have a measured reason.
        //
        // get(i)                 O(n)
        // add/remove at ends     O(1)
        // add/remove at index i  O(n) to find, O(1) to link
        // contains               O(n)
        // ============================================
    }
}
