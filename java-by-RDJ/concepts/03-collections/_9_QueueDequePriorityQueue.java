// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.*;

public class _9_QueueDequePriorityQueue {

    record Task(String name, int priority) {
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: QUEUE = FIRST IN, FIRST OUT (FIFO)
        // Add at the back, take from the front, like a line at a shop.
        // ============================================

        Queue<String> queue = new ArrayDeque<>();
        queue.offer("first");
        queue.offer("second");
        queue.offer("third");
        System.out.println("peek (look, do not remove): " + queue.peek());
        System.out.println("poll (remove front):         " + queue.poll());
        System.out.println("queue now: " + queue);


        // ============================================
        // SECTION 2: TWO FAMILIES OF METHODS
        // Most operations come in a pair: one THROWS when it cannot work,
        // one RETURNS a special value instead.
        //   add(x)     throws on failure     offer(x)   returns false
        //   remove()   throws if empty       poll()     returns null
        //   element()  throws if empty       peek()     returns null
        // ============================================

        Queue<String> empty = new ArrayDeque<>();
        System.out.println("poll on empty: " + empty.poll() + ", peek on empty: " + empty.peek());
        try {
            empty.remove();
        } catch (NoSuchElementException e) {
            System.out.println("remove() on empty threw NoSuchElementException");
        }


        // ============================================
        // SECTION 3: DEQUE = A QUEUE THAT WORKS AT BOTH ENDS
        // So it can also be used as a STACK (last in, first out).
        // Prefer ArrayDeque over the old Stack class (a legacy, synchronized
        // class built on Vector).
        // ============================================

        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(1);
        stack.push(2);
        stack.push(3);
        System.out.println("pop: " + stack.pop() + ", then pop: " + stack.pop());

        Deque<String> deque = new ArrayDeque<>();
        deque.offerFirst("B");
        deque.offerFirst("A");
        deque.offerLast("C");
        System.out.println("deque: " + deque + ", pollLast: " + deque.pollLast());

        try {
            deque.add(null);
        } catch (NullPointerException e) {
            System.out.println("ArrayDeque rejects null (poll() uses null to mean 'empty')");
        }


        // ============================================
        // SECTION 4: PriorityQueue = A QUEUE THAT ALWAYS HANDS BACK THE SMALLEST
        // Backed by a binary heap. poll() returns the element that is first in
        // sorted order, no matter what order things were added.
        // offer / poll are O(log n); peek is O(1).
        // ============================================

        PriorityQueue<Integer> pq = new PriorityQueue<>();
        for (int n : new int[]{5, 1, 4, 2, 3}) {
            pq.offer(n);
        }
        StringBuilder order = new StringBuilder();
        while (!pq.isEmpty()) {
            order.append(pq.poll()).append(' ');
        }
        System.out.println("poll order: " + order);


        // ============================================
        // SECTION 5: TRAP - PRINTING A PriorityQueue DOES NOT SHOW SORTED ORDER
        // Only the head is guaranteed to be the smallest. The rest is in heap
        // layout. Iteration and toString show that layout.
        // ============================================

        PriorityQueue<Integer> heap = new PriorityQueue<>();
        for (int n : new int[]{5, 1, 4, 2, 3}) {
            heap.offer(n);
        }
        System.out.println("printed heap: " + heap + "   <- NOT sorted, only the first element is guaranteed smallest");


        // ============================================
        // SECTION 6: CUSTOM ORDER - MAX-HEAP AND OBJECTS
        // ============================================

        PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
        maxHeap.addAll(List.of(5, 1, 4));
        System.out.println("max-heap first: " + maxHeap.peek());

        PriorityQueue<Task> tasks = new PriorityQueue<>(Comparator.comparingInt(Task::priority));
        tasks.offer(new Task("write report", 3));
        tasks.offer(new Task("fix outage", 1));
        tasks.offer(new Task("reply to email", 2));
        while (!tasks.isEmpty()) {
            System.out.println("  next: " + tasks.poll());
        }


        // ============================================
        // SECTION 7: CHOOSING
        // FIFO processing                 -> ArrayDeque (as a Queue)
        // Undo history / call stack       -> ArrayDeque (as a Deque, push/pop)
        // Always process the best first   -> PriorityQueue
        // ============================================
    }
}
