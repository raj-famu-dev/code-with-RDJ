// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayDeque;
import java.util.Random;

/**
 * STACK (last in, first out) and QUEUE (first in, first out). Built on arrays and nodes, no java.util collections
 * inside the structures (java.util.ArrayDeque is only the oracle in main()).
 *
 * Big-O (all O(1) unless noted):
 *   ArrayStack:    push (amortized O(1)), pop, peek, isEmpty
 *   LinkedQueue:   enqueue, dequeue, peek
 *   RingQueue:     enqueue (amortized O(1): resize doubles), dequeue, peek
 * Why a RING (circular) buffer? Removing from the front of a plain array would shift every element (O(n)).
 * A ring just moves a "head" index forward and wraps around using modulo.
 */
public class _3_StackAndQueue {

    // ============================================
    // STACK on an array
    // ============================================

    static class ArrayStack<T> {
        private Object[] data = new Object[4];
        private int size;

        void push(T value) {
            if (size == data.length) {
                Object[] bigger = new Object[size * 2];
                System.arraycopy(data, 0, bigger, 0, size);
                data = bigger;
            }
            data[size++] = value;
        }

        @SuppressWarnings("unchecked")
        T pop() {
            if (size == 0) throw new java.util.NoSuchElementException("stack is empty");
            T value = (T) data[--size];
            data[size] = null;                                     // do not keep a reference to a removed element
            return value;
        }

        @SuppressWarnings("unchecked")
        T peek() {
            if (size == 0) throw new java.util.NoSuchElementException("stack is empty");
            return (T) data[size - 1];
        }

        boolean isEmpty() {
            return size == 0;
        }

        int size() {
            return size;
        }
    }

    // ============================================
    // QUEUE on linked nodes (head = front, tail = back)
    // ============================================

    static class LinkedQueue<T> {
        private static class Node<T> {
            final T value;
            Node<T> next;

            Node(T value) {
                this.value = value;
            }
        }

        private Node<T> head;
        private Node<T> tail;
        private int size;

        void enqueue(T value) {
            Node<T> node = new Node<>(value);
            if (tail == null) {
                head = tail = node;
            } else {
                tail.next = node;
                tail = node;
            }
            size++;
        }

        T dequeue() {
            if (head == null) throw new java.util.NoSuchElementException("queue is empty");
            T value = head.value;
            head = head.next;
            if (head == null) tail = null;                         // emptied: reset the tail too
            size--;
            return value;
        }

        T peek() {
            if (head == null) throw new java.util.NoSuchElementException("queue is empty");
            return head.value;
        }

        boolean isEmpty() {
            return size == 0;
        }

        int size() {
            return size;
        }
    }

    // ============================================
    // QUEUE on a circular array ("ring buffer")
    // ============================================

    static class RingQueue<T> {
        private Object[] data = new Object[4];
        private int head;                                          // index of the front element
        private int size;

        void enqueue(T value) {
            if (size == data.length) grow();
            data[(head + size) % data.length] = value;             // the back, wrapped around the end of the array
            size++;
        }

        @SuppressWarnings("unchecked")
        T dequeue() {
            if (size == 0) throw new java.util.NoSuchElementException("queue is empty");
            T value = (T) data[head];
            data[head] = null;
            head = (head + 1) % data.length;                       // move forward, wrap at the end
            size--;
            return value;
        }

        @SuppressWarnings("unchecked")
        T peek() {
            if (size == 0) throw new java.util.NoSuchElementException("queue is empty");
            return (T) data[head];
        }

        boolean isEmpty() {
            return size == 0;
        }

        int size() {
            return size;
        }

        private void grow() {
            Object[] bigger = new Object[data.length * 2];
            for (int i = 0; i < size; i++) {
                bigger[i] = data[(head + i) % data.length];        // UNWRAP: copy in logical order, starting at 0
            }
            data = bigger;
            head = 0;                                              // after unwrapping, the front is at index 0 again
        }

        String layout() {                                          // shows the physical array, to see the wrap-around
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < data.length; i++) {
                sb.append(data[i] == null ? "_" : data[i]).append(i < data.length - 1 ? " " : "");
            }
            return sb.append("] head=").append(head).append(" size=").append(size).toString();
        }
    }

    // ============================================
    // CLASSIC USES
    // ============================================

    // 1) STACK: are the brackets balanced?
    static boolean isBalanced(String text) {
        ArrayStack<Character> open = new ArrayStack<>();
        for (char c : text.toCharArray()) {
            if (c == '(' || c == '[' || c == '{') {
                open.push(c);
            } else if (c == ')' || c == ']' || c == '}') {
                if (open.isEmpty()) return false;
                char left = open.pop();
                if ((c == ')' && left != '(') || (c == ']' && left != '[') || (c == '}' && left != '{')) return false;
            }
        }
        return open.isEmpty();
    }

    // 2) STACK: evaluate a postfix ("reverse Polish") expression such as "3 4 + 2 *" = (3+4)*2
    static int evalPostfix(String expression) {
        ArrayStack<Integer> stack = new ArrayStack<>();
        for (String token : expression.trim().split("\\s+")) {
            switch (token) {
                case "+", "-", "*", "/" -> {
                    int right = stack.pop();                       // the RIGHT operand comes off first
                    int left = stack.pop();
                    stack.push(switch (token) {
                        case "+" -> left + right;
                        case "-" -> left - right;
                        case "*" -> left * right;
                        default -> left / right;
                    });
                }
                default -> stack.push(Integer.parseInt(token));
            }
        }
        if (stack.size() != 1) throw new IllegalArgumentException("malformed expression: " + expression);
        return stack.pop();
    }

    // 3) QUEUE: the "Josephus" game: people stand in a circle, every k-th is eliminated. Who survives?
    static int lastSurvivor(int people, int k) {
        RingQueue<Integer> circle = new RingQueue<>();
        for (int i = 1; i <= people; i++) circle.enqueue(i);
        while (circle.size() > 1) {
            for (int skip = 1; skip < k; skip++) {
                circle.enqueue(circle.dequeue());                  // move the front person to the back
            }
            circle.dequeue();                                      // eliminate the k-th
        }
        return circle.dequeue();
    }

    public static void main(String[] args) {

        System.out.println("=== stack ===");
        ArrayStack<String> stack = new ArrayStack<>();
        stack.push("a");
        stack.push("b");
        stack.push("c");
        System.out.println("peek = " + stack.peek() + ", pop = " + stack.pop() + ", pop = " + stack.pop() + ", size = " + stack.size());
        try {
            new ArrayStack<Integer>().pop();
        } catch (java.util.NoSuchElementException e) {
            System.out.println("NoSuchElementException: " + e.getMessage());
        }
        System.out.println("balanced \"{[()]}\"  : " + isBalanced("{[()]}"));
        System.out.println("balanced \"{[(])}\"  : " + isBalanced("{[(])}"));
        System.out.println("balanced \"((\"      : " + isBalanced("(("));
        System.out.println("postfix \"3 4 + 2 *\"     = " + evalPostfix("3 4 + 2 *"));
        System.out.println("postfix \"5 1 2 + 4 * + 3 -\" = " + evalPostfix("5 1 2 + 4 * + 3 -"));

        System.out.println("=== linked queue ===");
        LinkedQueue<Integer> lq = new LinkedQueue<>();
        for (int i = 1; i <= 3; i++) lq.enqueue(i);
        System.out.println("dequeue order: " + lq.dequeue() + ", " + lq.dequeue() + ", " + lq.dequeue() + ", isEmpty = " + lq.isEmpty());
        lq.enqueue(9);
        System.out.println("re-used after emptying: peek = " + lq.peek());

        System.out.println("=== ring queue: watch the physical array wrap around ===");
        RingQueue<String> ring = new RingQueue<>();
        ring.enqueue("A");
        ring.enqueue("B");
        ring.enqueue("C");
        ring.enqueue("D");
        System.out.println("full:             " + ring.layout());
        ring.dequeue();
        ring.dequeue();
        System.out.println("after 2 dequeues: " + ring.layout());
        ring.enqueue("E");
        ring.enqueue("F");
        System.out.println("E and F WRAPPED:  " + ring.layout() + "   (back of the queue is at the start of the array)");
        ring.enqueue("G");
        System.out.println("grew and unwrapped: " + ring.layout());
        StringBuilder order = new StringBuilder();
        while (!ring.isEmpty()) order.append(ring.dequeue());
        System.out.println("dequeued in order: " + order);

        System.out.println("=== Josephus (every 3rd of 7 people eliminated) ===");
        System.out.println("survivor among 7 with k=3: person " + lastSurvivor(7, 3));
        System.out.println("survivor among 41 with k=3: person " + lastSurvivor(41, 3));

        // ---------- ORACLE TEST vs java.util.ArrayDeque ----------
        Random random = new Random(2024);
        RingQueue<Integer> r = new RingQueue<>();
        LinkedQueue<Integer> l = new LinkedQueue<>();
        ArrayStack<Integer> s = new ArrayStack<>();
        ArrayDeque<Integer> queueOracle = new ArrayDeque<>();
        ArrayDeque<Integer> stackOracle = new ArrayDeque<>();
        boolean ok = true;
        for (int step = 0; step < 20_000; step++) {
            if (random.nextInt(3) != 0 || queueOracle.isEmpty()) {
                int v = random.nextInt(1000);
                r.enqueue(v);
                l.enqueue(v);
                s.push(v);
                queueOracle.addLast(v);
                stackOracle.push(v);
            } else {
                int expected = queueOracle.pollFirst();
                ok &= r.dequeue() == expected && l.dequeue() == expected;
                ok &= s.pop().equals(stackOracle.pop());           // .equals, NOT ==: two Integer objects above 127 are different objects
                // the stack and the queue hold the same VALUES but pop them in different orders, so each
                // is compared with its own oracle; both are pushed and popped in the same steps, so sizes stay equal
            }
            ok &= r.size() == queueOracle.size() && l.size() == queueOracle.size();
        }
        System.out.println("oracle test: 20000 random operations, ring queue, linked queue and stack match: " + ok);

        // ============================================
        // THINGS TO BREAK ON PURPOSE
        // 1) In RingQueue.grow(): copy with System.arraycopy(data, 0, bigger, 0, size) instead of unwrapping.
        //    It works until the queue has wrapped. Then the order is wrong. (Make a test that finds it.)
        // 2) In LinkedQueue.dequeue(): delete `if (head == null) tail = null` and enqueue after emptying.
        // 3) In evalPostfix: pop left before right. Try "5 3 -".
        // ============================================
    }
}
