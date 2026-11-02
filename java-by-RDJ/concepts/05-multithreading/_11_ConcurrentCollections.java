// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.ArrayList;
import java.util.ConcurrentModificationException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

public class _11_ConcurrentCollections {

    static void hammer(Runnable op, int threads) throws InterruptedException {
        Thread[] workers = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            workers[i] = new Thread(op);
        }
        for (Thread t : workers) t.start();
        for (Thread t : workers) t.join();
    }

    public static void main(String[] args) throws Exception {

        // ============================================
        // SECTION 1: ORDINARY COLLECTIONS ARE NOT THREAD-SAFE
        // HashMap, ArrayList and friends have no locking. Two threads changing
        // one at the same time can lose updates or corrupt it. The java.util.concurrent
        // package has versions designed for sharing between threads.
        // ============================================

        Map<String, Integer> plain = new HashMap<>();
        // Even "just counting" is a read-modify-write on the map: unsafe with HashMap.
        // (Not run on purpose: the result is unpredictable, and with a plain HashMap
        // the failure modes include lost updates and corrupted internal state.)


        // ============================================
        // SECTION 2: ConcurrentHashMap
        // Thread-safe, and it does NOT lock the whole map for every operation.
        // The key trick is the ATOMIC methods: merge, compute, putIfAbsent.
        // map.put(k, map.get(k) + 1) is still a race; map.merge(k, 1, Integer::sum) is not.
        // ============================================

        ConcurrentHashMap<String, Integer> counts = new ConcurrentHashMap<>();
        hammer(() -> {
            for (int i = 0; i < 10_000; i++) {
                counts.merge("hits", 1, Integer::sum);
            }
        }, 4);
        System.out.println("ConcurrentHashMap merge: " + counts.get("hits") + " (expected 40000)");

        counts.putIfAbsent("hits", 0);                              // already present: no change
        counts.putIfAbsent("misses", 0);                            // absent: inserted
        System.out.println("after putIfAbsent: " + new java.util.TreeMap<>(counts));

        try {
            counts.put(null, 1);                                    // ConcurrentHashMap forbids null keys and values
        } catch (NullPointerException e) {
            System.out.println("NullPointerException: ConcurrentHashMap does not allow null keys or values");
        }


        // ============================================
        // SECTION 3: THE ConcurrentModificationException TRAP
        // Changing a list while looping over it fails, even in ONE thread.
        // ============================================

        List<Integer> normal = new ArrayList<>(List.of(1, 2, 3));
        try {
            for (Integer n : normal) {
                if (n == 2) normal.add(99);
            }
        } catch (ConcurrentModificationException e) {
            System.out.println("ArrayList: ConcurrentModificationException while modifying during iteration");
        }


        // ============================================
        // SECTION 4: CopyOnWriteArrayList
        // Every write makes a fresh COPY of the whole array; iterators work on the
        // snapshot they started with, so they never fail. Perfect for lists that are
        // read and iterated a lot and changed rarely (e.g. listeners). Bad for heavy writing.
        // ============================================

        List<Integer> snapshot = new CopyOnWriteArrayList<>(List.of(1, 2, 3));
        for (Integer n : snapshot) {
            if (n == 2) snapshot.add(99);                           // allowed: loop still sees the OLD 3 items
        }
        System.out.println("CopyOnWriteArrayList after the loop: " + snapshot);


        // ============================================
        // SECTION 5: BlockingQueue - PRODUCER/CONSUMER WITHOUT wait/notify
        // The _7 buffer, ready-made. put() waits when full; take() waits when empty.
        // ============================================

        BlockingQueue<Integer> queue = new ArrayBlockingQueue<>(3);
        int poison = -1;
        List<Integer> received = new ArrayList<>();

        Thread producer = new Thread(() -> {
            try {
                for (int i = 1; i <= 8; i++) {
                    queue.put(i);
                }
                queue.put(poison);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        Thread consumer = new Thread(() -> {
            try {
                int v;
                while ((v = queue.take()) != poison) {
                    received.add(v);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        producer.start();
        consumer.start();
        producer.join();
        consumer.join();
        System.out.println("BlockingQueue delivered: " + received);

        // offer/poll with a timeout instead of waiting forever
        BlockingQueue<String> empty = new ArrayBlockingQueue<>(1);
        System.out.println("poll(50 ms) on an empty queue: " + empty.poll(50, TimeUnit.MILLISECONDS));
        empty.put("x");
        System.out.println("offer(\"y\") on a full queue:   " + empty.offer("y"));


        // ============================================
        // SECTION 6: CountDownLatch - "WAIT UNTIL N THINGS HAVE HAPPENED"
        // Three workers each call countDown(); main's await() returns when it hits 0.
        // A latch is single-use (it cannot be reset).
        // ============================================

        CountDownLatch done = new CountDownLatch(3);
        for (int i = 1; i <= 3; i++) {
            new Thread(done::countDown).start();
        }
        boolean allDone = done.await(2, TimeUnit.SECONDS);
        System.out.println("latch released (all 3 workers finished): " + allDone);


        // ============================================
        // SECTION 7: Collections.synchronizedList - THE OLD WAY
        // Wraps every method in synchronized. Single operations are safe, but
        // looping over it still needs a manual synchronized(list) block, and it
        // locks the whole list. Prefer the java.util.concurrent classes.
        // ============================================
    }
}
