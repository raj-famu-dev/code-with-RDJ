// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * LINKED LISTS: nodes connected by references. Singly (next only), then doubly (next and prev).
 * NO java.util collections inside the structures; java.util.ArrayList is only the oracle in main().
 *
 * Big-O singly linked list WITH a head pointer only (n = size):
 *   addFirst, removeFirst               O(1)
 *   addLast                             O(n)   (must walk to the end)   <- O(1) if you also keep a tail
 *   get(i), insert(i), remove(i)        O(n)   (must walk to position i)
 *   contains                            O(n)
 *   reverse                             O(n) time, O(1) extra space
 * Doubly linked list WITH head AND tail:
 *   addFirst, addLast, removeFirst, removeLast   O(1)
 *   remove a node you already hold               O(1)
 *   get(i)                                       O(n) (walks from the nearer end)
 * Versus array: no O(1) random access, extra memory per node (a Node object plus references), poor cache locality.
 */
public class _2_LinkedList {

    // ============================================
    // PART 1: SINGLY LINKED LIST
    // ============================================

    static class SinglyLinkedList<T> {
        static class Node<T> {
            T value;
            Node<T> next;

            Node(T value) {
                this.value = value;
            }
        }

        Node<T> head;
        private int size;

        int size() {
            return size;
        }

        void addFirst(T value) {
            Node<T> node = new Node<>(value);
            node.next = head;
            head = node;
            size++;
        }

        void addLast(T value) {
            Node<T> node = new Node<>(value);
            if (head == null) {
                head = node;
            } else {
                Node<T> current = head;
                while (current.next != null) {                     // walk to the last node: O(n)
                    current = current.next;
                }
                current.next = node;
            }
            size++;
        }

        T removeFirst() {
            if (head == null) throw new java.util.NoSuchElementException("list is empty");
            T value = head.value;
            head = head.next;
            size--;
            return value;
        }

        T get(int index) {
            return nodeAt(index).value;
        }

        void insert(int index, T value) {
            if (index < 0 || index > size) throw new IndexOutOfBoundsException("index " + index + ", size " + size);
            if (index == 0) {
                addFirst(value);
                return;
            }
            Node<T> before = nodeAt(index - 1);
            Node<T> node = new Node<>(value);
            node.next = before.next;                               // 1) new node points at what followed
            before.next = node;                                    // 2) predecessor points at the new node (ORDER MATTERS)
            size++;
        }

        T remove(int index) {
            if (index < 0 || index >= size) throw new IndexOutOfBoundsException("index " + index + ", size " + size);
            if (index == 0) return removeFirst();
            Node<T> before = nodeAt(index - 1);
            T value = before.next.value;
            before.next = before.next.next;                        // skip over the removed node
            size--;
            return value;
        }

        boolean contains(T value) {
            for (Node<T> n = head; n != null; n = n.next) {
                if (n.value == null ? value == null : n.value.equals(value)) return true;
            }
            return false;
        }

        // Reverse in place by flipping each next pointer. Three references: previous, current, next.
        void reverse() {
            Node<T> previous = null;
            Node<T> current = head;
            while (current != null) {
                Node<T> next = current.next;                       // remember the rest BEFORE breaking the link
                current.next = previous;                           // flip
                previous = current;
                current = next;
            }
            head = previous;
        }

        // Fast/slow pointers: when fast reaches the end, slow is in the middle. One pass, O(1) space.
        T middle() {
            if (head == null) throw new java.util.NoSuchElementException("list is empty");
            Node<T> slow = head;
            Node<T> fast = head;
            while (fast.next != null && fast.next.next != null) {
                slow = slow.next;
                fast = fast.next.next;
            }
            return slow.value;
        }

        private Node<T> nodeAt(int index) {
            if (index < 0 || index >= size) throw new IndexOutOfBoundsException("index " + index + ", size " + size);
            Node<T> current = head;
            for (int i = 0; i < index; i++) current = current.next;
            return current;
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            for (Node<T> n = head; n != null; n = n.next) {
                sb.append(n.value).append(n.next != null ? " -> " : "");
            }
            return sb.length() == 0 ? "(empty)" : sb.toString();
        }
    }

    // Floyd's cycle detection ("tortoise and hare"): if there is a loop, fast eventually laps slow.
    static <T> boolean hasCycle(SinglyLinkedList.Node<T> head) {
        SinglyLinkedList.Node<T> slow = head;
        SinglyLinkedList.Node<T> fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) return true;
        }
        return false;
    }

    // ============================================
    // PART 2: DOUBLY LINKED LIST with head AND tail
    // ============================================

    static class DoublyLinkedList<T> {
        private static class Node<T> {
            T value;
            Node<T> prev;
            Node<T> next;

            Node(T value) {
                this.value = value;
            }
        }

        private Node<T> head;
        private Node<T> tail;
        private int size;

        int size() {
            return size;
        }

        void addFirst(T value) {
            Node<T> node = new Node<>(value);
            if (head == null) {
                head = tail = node;
            } else {
                node.next = head;
                head.prev = node;
                head = node;
            }
            size++;
        }

        void addLast(T value) {
            Node<T> node = new Node<>(value);
            if (tail == null) {
                head = tail = node;
            } else {
                node.prev = tail;
                tail.next = node;
                tail = node;
            }
            size++;
        }

        T removeFirst() {
            if (head == null) throw new java.util.NoSuchElementException("list is empty");
            T value = head.value;
            head = head.next;
            if (head == null) tail = null;                         // the list became empty: BOTH ends reset
            else head.prev = null;
            size--;
            return value;
        }

        T removeLast() {
            if (tail == null) throw new java.util.NoSuchElementException("list is empty");
            T value = tail.value;
            tail = tail.prev;
            if (tail == null) head = null;
            else tail.next = null;
            size--;
            return value;
        }

        T get(int index) {
            if (index < 0 || index >= size) throw new IndexOutOfBoundsException("index " + index + ", size " + size);
            Node<T> current;
            if (index < size / 2) {                                // start from whichever end is nearer
                current = head;
                for (int i = 0; i < index; i++) current = current.next;
            } else {
                current = tail;
                for (int i = size - 1; i > index; i--) current = current.prev;
            }
            return current.value;
        }

        String forward() {
            StringBuilder sb = new StringBuilder();
            for (Node<T> n = head; n != null; n = n.next) sb.append(n.value).append(n.next != null ? " <-> " : "");
            return sb.length() == 0 ? "(empty)" : sb.toString();
        }

        String backward() {
            StringBuilder sb = new StringBuilder();
            for (Node<T> n = tail; n != null; n = n.prev) sb.append(n.value).append(n.prev != null ? " <-> " : "");
            return sb.length() == 0 ? "(empty)" : sb.toString();
        }
    }

    public static void main(String[] args) {

        System.out.println("=== singly linked list ===");
        SinglyLinkedList<Integer> list = new SinglyLinkedList<>();
        list.addLast(2);
        list.addLast(3);
        list.addFirst(1);
        list.addLast(4);
        list.addLast(5);
        System.out.println("list:             " + list + "  (size " + list.size() + ")");
        list.insert(2, 99);
        System.out.println("insert(2, 99):    " + list);
        int removed = list.remove(2);
        System.out.println("remove(2) returned " + removed + ", list is now: " + list);
        System.out.println("middle():         " + list.middle());
        list.reverse();
        System.out.println("reversed:         " + list);
        System.out.println("contains(3) = " + list.contains(3) + ", contains(42) = " + list.contains(42));
        try {
            list.get(9);
        } catch (IndexOutOfBoundsException e) {
            System.out.println("IndexOutOfBoundsException: " + e.getMessage());
        }
        try {
            new SinglyLinkedList<String>().removeFirst();
        } catch (java.util.NoSuchElementException e) {
            System.out.println("NoSuchElementException: " + e.getMessage());
        }

        // cycle detection: build a loop by hand (tail points back to the second node)
        SinglyLinkedList<Integer> loop = new SinglyLinkedList<>();
        for (int i = 1; i <= 5; i++) loop.addLast(i);
        System.out.println("hasCycle (normal list): " + hasCycle(loop.head));
        SinglyLinkedList.Node<Integer> last = loop.head;
        while (last.next != null) last = last.next;
        last.next = loop.head.next;                                // 5 -> 2 : a cycle
        System.out.println("hasCycle (5 points back to 2): " + hasCycle(loop.head));
        // (do NOT print this list: toString would loop forever)

        System.out.println("=== doubly linked list ===");
        DoublyLinkedList<String> dll = new DoublyLinkedList<>();
        dll.addLast("b");
        dll.addLast("c");
        dll.addFirst("a");
        dll.addLast("d");
        System.out.println("forward:  " + dll.forward());
        System.out.println("backward: " + dll.backward());
        String first = dll.removeFirst();
        String last2 = dll.removeLast();
        System.out.println("removeFirst returned " + first + ", removeLast returned " + last2 + ", list is now: " + dll.forward());
        System.out.println("get(0) = " + dll.get(0) + ", get(1) = " + dll.get(1));
        dll.removeFirst();
        dll.removeFirst();
        System.out.println("emptied: " + dll.forward() + ", adding after emptying works: " + tryReuse(dll));

        // ---------- ORACLE TEST: random operations vs java.util.ArrayList ----------
        Random random = new Random(777);
        SinglyLinkedList<Integer> s = new SinglyLinkedList<>();
        DoublyLinkedList<Integer> d = new DoublyLinkedList<>();
        List<Integer> oracle = new ArrayList<>();
        boolean ok = true;
        for (int step = 0; step < 5_000; step++) {
            int v = random.nextInt(100);
            switch (random.nextInt(4)) {
                case 0 -> {
                    s.addFirst(v);
                    d.addFirst(v);
                    oracle.add(0, v);
                }
                case 1 -> {
                    s.addLast(v);
                    d.addLast(v);
                    oracle.add(v);
                }
                case 2 -> {
                    if (!oracle.isEmpty()) {
                        int a = s.removeFirst();
                        int b = d.removeFirst();
                        int c = oracle.remove(0);
                        ok &= a == c && b == c;
                    }
                }
                default -> {
                    if (!oracle.isEmpty()) {
                        int index = random.nextInt(oracle.size());
                        ok &= s.get(index).equals(oracle.get(index)) && d.get(index).equals(oracle.get(index));
                    }
                }
            }
            ok &= s.size() == oracle.size() && d.size() == oracle.size();
        }
        System.out.println("oracle test: 5000 random operations, singly and doubly match ArrayList: " + ok);

        // ============================================
        // THINGS TO BREAK ON PURPOSE
        // 1) In insert(): swap the two pointer lines. You lose the rest of the list. Why?
        // 2) In reverse(): delete the "remember the rest" line. What does the list look like?
        // 3) In removeFirst() of the doubly list: delete `if (head == null) tail = null`. Add after emptying.
        // ============================================
    }

    static boolean tryReuse(DoublyLinkedList<String> dll) {
        dll.addLast("again");
        return dll.size() == 1 && dll.get(0).equals("again");
    }
}
