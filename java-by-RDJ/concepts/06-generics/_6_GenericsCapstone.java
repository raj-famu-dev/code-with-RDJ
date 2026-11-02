// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.NoSuchElementException;

/**
 * CAPSTONE: build your own generic Stack<T> and Queue<T> on top of a linked chain
 * of nodes (no java.util collections inside), then use PECS wildcards to move items
 * between them. Uses: generic classes, generic inner types, bounded types, wildcards.
 */
public class _6_GenericsCapstone {

    // A node in a chain. Private to this file's structures, generic in its own right.
    private static class Node<T> {
        final T value;
        Node<T> next;

        Node(T value) {
            this.value = value;
        }
    }

    // ============================================
    // PART 1: Stack<T>  (last in, first out) - a singly linked chain, push at the head
    // ============================================

    static class Stack<T> implements Iterable<T> {
        private Node<T> top;
        private int size;

        void push(T item) {
            Node<T> node = new Node<>(item);
            node.next = top;
            top = node;
            size++;
        }

        T pop() {
            if (top == null) {
                throw new NoSuchElementException("stack is empty");
            }
            T value = top.value;
            top = top.next;
            size--;
            return value;
        }

        T peek() {
            if (top == null) {
                throw new NoSuchElementException("stack is empty");
            }
            return top.value;
        }

        boolean isEmpty() {
            return size == 0;
        }

        int size() {
            return size;
        }

        // PECS: we only READ from 'items' (producer), so ? extends T
        void pushAll(Collection<? extends T> items) {
            for (T item : items) {
                push(item);
            }
        }

        // PECS: we WRITE into 'target' (consumer), so ? super T
        void popAllInto(Collection<? super T> target) {
            while (!isEmpty()) {
                target.add(pop());
            }
        }

        @Override
        public java.util.Iterator<T> iterator() {
            return new java.util.Iterator<>() {
                private Node<T> current = top;

                @Override
                public boolean hasNext() {
                    return current != null;
                }

                @Override
                public T next() {
                    if (current == null) {
                        throw new NoSuchElementException();
                    }
                    T value = current.value;
                    current = current.next;
                    return value;
                }
            };
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder("Stack(top -> bottom)[");
            for (T item : this) {
                sb.append(item).append(' ');
            }
            return sb.toString().trim() + "]";
        }
    }

    // ============================================
    // PART 2: Queue<T>  (first in, first out) - keeps a head AND a tail pointer
    // ============================================

    static class Queue<T> implements Iterable<T> {
        private Node<T> head;
        private Node<T> tail;
        private int size;

        void enqueue(T item) {
            Node<T> node = new Node<>(item);
            if (tail == null) {
                head = node;
            } else {
                tail.next = node;
            }
            tail = node;
            size++;
        }

        T dequeue() {
            if (head == null) {
                throw new NoSuchElementException("queue is empty");
            }
            T value = head.value;
            head = head.next;
            if (head == null) {
                tail = null;                              // queue became empty: reset the tail too
            }
            size--;
            return value;
        }

        T peek() {
            if (head == null) {
                throw new NoSuchElementException("queue is empty");
            }
            return head.value;
        }

        boolean isEmpty() {
            return size == 0;
        }

        int size() {
            return size;
        }

        @Override
        public java.util.Iterator<T> iterator() {
            return new java.util.Iterator<>() {
                private Node<T> current = head;

                @Override
                public boolean hasNext() {
                    return current != null;
                }

                @Override
                public T next() {
                    if (current == null) {
                        throw new NoSuchElementException();
                    }
                    T value = current.value;
                    current = current.next;
                    return value;
                }
            };
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder("Queue(head -> tail)[");
            for (T item : this) {
                sb.append(item).append(' ');
            }
            return sb.toString().trim() + "]";
        }
    }

    // ============================================
    // PART 3: A BOUNDED GENERIC HELPER
    // The biggest value in any Iterable of comparable things. 'Comparable<? super T>'
    // is the library-grade form of the bound: it also accepts a subclass whose
    // PARENT implements Comparable.
    // ============================================

    static <T extends Comparable<? super T>> T largest(Iterable<T> items) {
        T best = null;
        for (T item : items) {
            if (best == null || item.compareTo(best) > 0) {
                best = item;
            }
        }
        if (best == null) {
            throw new NoSuchElementException("nothing to compare");
        }
        return best;
    }

    // ============================================
    // PART 4: A CLASSIC USE OF A STACK - checking balanced brackets
    // ============================================

    static boolean isBalanced(String text) {
        Stack<Character> open = new Stack<>();
        for (char c : text.toCharArray()) {
            switch (c) {
                case '(', '[', '{' -> open.push(c);
                case ')', ']', '}' -> {
                    if (open.isEmpty()) return false;
                    char left = open.pop();
                    boolean matches = (left == '(' && c == ')') || (left == '[' && c == ']') || (left == '{' && c == '}');
                    if (!matches) return false;
                }
                default -> { }
            }
        }
        return open.isEmpty();
    }

    public static void main(String[] args) {

        // --- Stack ---
        Stack<String> stack = new Stack<>();
        stack.push("a");
        stack.push("b");
        stack.push("c");
        System.out.println(stack + ", size " + stack.size());
        System.out.println("pop  = " + stack.pop());
        System.out.println("peek = " + stack.peek());

        // --- Queue ---
        Queue<Integer> queue = new Queue<>();
        queue.enqueue(1);
        queue.enqueue(2);
        queue.enqueue(3);
        System.out.println(queue + ", size " + queue.size());
        System.out.println("dequeue = " + queue.dequeue());
        System.out.println("peek    = " + queue.peek());
        queue.dequeue();
        queue.dequeue();
        System.out.println("emptied: isEmpty = " + queue.isEmpty());
        queue.enqueue(99);                                // works again after becoming empty (tail was reset)
        System.out.println("after re-use: " + queue);

        // --- Empty-structure errors ---
        try {
            new Stack<Double>().pop();
        } catch (NoSuchElementException e) {
            System.out.println("pop on empty: " + e.getMessage());
        }

        // --- PECS in action ---
        Stack<Number> numbers = new Stack<>();
        List<Integer> ints = List.of(1, 2, 3);
        List<Double> doubles = List.of(0.5, 1.5);
        numbers.pushAll(ints);                            // Integers into a Stack<Number>: ? extends T
        numbers.pushAll(doubles);                         // Doubles too
        System.out.println(numbers);

        List<Object> sink = new ArrayList<>();
        numbers.popAllInto(sink);                         // Numbers into a List<Object>: ? super T
        System.out.println("popped everything into List<Object>: " + sink);

        // --- bounded helper ---
        Queue<String> words = new Queue<>();
        for (String w : List.of("kiwi", "apple", "zebra", "mango")) {
            words.enqueue(w);
        }
        System.out.println("largest word  = " + largest(words));
        Stack<Integer> nums = new Stack<>();
        nums.pushAll(List.of(7, 42, 13));
        System.out.println("largest number = " + largest(nums));

        // --- Stack in a real algorithm ---
        for (String s : List.of("([]{})", "(]", "((", "")) {
            System.out.println("isBalanced(\"" + s + "\") = " + isBalanced(s));
        }

        // Compile-time safety, still ours:
        // stack.push(5);                                 // COMPILE ERROR: stack holds Strings
        // Queue<int> bad;                                // COMPILE ERROR: no primitives as type arguments
    }
}
