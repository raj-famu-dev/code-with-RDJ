// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

public class _7_WaitNotify {

    // A bounded buffer: producers wait when it is full, consumers wait when it is empty
    static class BoundedBuffer {
        private final Queue<Integer> items = new LinkedList<>();
        private final int capacity;

        BoundedBuffer(int capacity) {
            this.capacity = capacity;
        }

        synchronized void put(int value) throws InterruptedException {
            while (items.size() == capacity) {      // 'while', NOT 'if' (see Section 4)
                wait();                             // releases the lock and sleeps
            }
            items.add(value);
            notifyAll();                            // wake threads waiting for "not empty"
        }

        synchronized int take() throws InterruptedException {
            while (items.isEmpty()) {
                wait();
            }
            int value = items.remove();
            notifyAll();                            // wake threads waiting for "not full"
            return value;
        }
    }

    public static void main(String[] args) throws InterruptedException {

        // ============================================
        // SECTION 1: THE PROBLEM wait/notify SOLVES
        // A consumer needs data that a producer has not made yet. Looping and
        // checking constantly ("busy waiting") burns CPU. Instead the consumer
        // WAITS, and the producer NOTIFIES it when something changes.
        // ============================================


        // ============================================
        // SECTION 2: THE RULES
        // - wait(), notify(), notifyAll() are methods of Object.
        // - You must hold that object's lock (be inside synchronized on it).
        // - wait() RELEASES the lock while sleeping and re-takes it before returning.
        // - notify() wakes ONE waiting thread; notifyAll() wakes ALL of them.
        // ============================================

        try {
            new Object().wait();                    // not inside synchronized
        } catch (IllegalMonitorStateException e) {
            System.out.println("Caught IllegalMonitorStateException: wait() needs the lock first");
        }


        // ============================================
        // SECTION 3: PRODUCER-CONSUMER
        // Buffer holds at most 3 items. Producer makes 1..8 and then -1 as a
        // "stop" signal (poison value). The consumer takes until it sees -1.
        // The printed lines from each thread may interleave differently each
        // run, but the consumer ALWAYS receives the values in the same order.
        // ============================================

        BoundedBuffer buffer = new BoundedBuffer(3);
        List<Integer> consumed = new ArrayList<>();

        Thread producer = new Thread(() -> {
            try {
                for (int i = 1; i <= 8; i++) {
                    buffer.put(i);
                }
                buffer.put(-1);                     // poison value: "no more data"
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "producer");

        Thread consumer = new Thread(() -> {
            try {
                while (true) {
                    int value = buffer.take();
                    if (value == -1) break;
                    consumed.add(value);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "consumer");

        producer.start();
        consumer.start();
        producer.join();
        consumer.join();
        System.out.println("consumed in order: " + consumed);


        // ============================================
        // SECTION 4: WHY A while LOOP AROUND wait(), NOT AN if
        // - Spurious wakeups: a waiting thread can wake up for no reason at all.
        // - Another thread may grab the item between the notify and your wake-up.
        // So after waking, ALWAYS re-check the condition:
        //     while (!conditionIsTrue) wait();
        // ============================================


        // ============================================
        // SECTION 5: notify vs notifyAll
        // notify() wakes just one thread, which might be the WRONG kind (a
        // producer woken when only consumers can make progress), leaving the
        // program stuck. notifyAll() is the safe default.
        // ============================================


        // ============================================
        // SECTION 6: IN REAL CODE
        // Hand-written wait/notify is easy to get wrong. Prefer a ready-made
        // BlockingQueue (see _11_ConcurrentCollections), which does exactly
        // this for you. Learning wait/notify shows what those classes do inside.
        // ============================================
    }
}
