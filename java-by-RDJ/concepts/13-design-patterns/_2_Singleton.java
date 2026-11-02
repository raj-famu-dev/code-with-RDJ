// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * SINGLETON: a class with exactly ONE instance and a global access point.
 * PROBLEM  : some things should exist once (a configuration, a connection pool, a logger).
 * SOLUTION : hide the constructor and hand out the single instance.
 * TRADE-OFF: it is a global variable in disguise: hard to test, hides dependencies, and creates
 *            tight coupling. Often dependency injection (_1, the D in SOLID) is the better answer.
 */
public class _2_Singleton {

    // counts how many times each version's constructor ran (should be 1 each)
    static final AtomicInteger eagerCreated = new AtomicInteger();
    static final AtomicInteger lazyCreated = new AtomicInteger();
    static final AtomicInteger holderCreated = new AtomicInteger();

    // ============================================
    // VERSION 1: EAGER - created when the class loads
    // Simple and thread-safe (the JVM guarantees class loading is safe).
    // Cost: created even if nobody ever uses it.
    // ============================================

    static class EagerConfig {
        private static final EagerConfig INSTANCE = new EagerConfig();

        private EagerConfig() {                                    // private: nobody else can call new
            eagerCreated.incrementAndGet();
        }

        static EagerConfig getInstance() {
            return INSTANCE;
        }
    }

    // ============================================
    // VERSION 2: LAZY + synchronized (and the broken lazy version it replaces)
    // Created on first use. The naive version (if (instance == null) instance = new ...) is NOT
    // thread-safe: two threads can both see null and each create one.
    // Here the method is synchronized: correct, but EVERY call pays for the lock.
    // Double-checked locking avoids that, but only works with a volatile field.
    // ============================================

    static class LazyConfig {
        private static volatile LazyConfig instance;               // volatile is REQUIRED for double-checked locking

        private LazyConfig() {
            lazyCreated.incrementAndGet();
        }

        static LazyConfig getInstance() {
            LazyConfig local = instance;                           // first check, no lock
            if (local == null) {
                synchronized (LazyConfig.class) {
                    local = instance;
                    if (local == null) {                           // second check, under the lock
                        instance = local = new LazyConfig();
                    }
                }
            }
            return local;
        }
    }

    // ============================================
    // VERSION 3: INITIALIZATION-ON-DEMAND HOLDER - lazy, thread-safe, no locks written by you
    // The nested Holder class is not loaded until getInstance() first touches it,
    // and class loading is guaranteed to be thread-safe.
    // ============================================

    static class HolderConfig {
        private HolderConfig() {
            holderCreated.incrementAndGet();
        }

        private static class Holder {
            static final HolderConfig INSTANCE = new HolderConfig();
        }

        static HolderConfig getInstance() {
            return Holder.INSTANCE;
        }
    }

    // ============================================
    // VERSION 4: AN ENUM SINGLETON - the shortest, and the safest
    // The JVM guarantees one instance, even against serialization and reflection tricks that can
    // create a second copy of a normal class. Cannot extend another class.
    // ============================================

    enum EnumConfig {
        INSTANCE;

        private String mode = "default";

        String mode() {
            return mode;
        }

        void setMode(String mode) {
            this.mode = mode;
        }
    }

    static void hammer(Runnable task, int threads) throws InterruptedException {
        CountDownLatch startGun = new CountDownLatch(1);
        Thread[] workers = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            workers[i] = new Thread(() -> {
                try {
                    startGun.await();                              // all threads start at the same instant
                } catch (InterruptedException e) {
                    return;
                }
                task.run();
            });
            workers[i].start();
        }
        startGun.countDown();
        for (Thread t : workers) t.join();
    }

    public static void main(String[] args) throws Exception {

        // ---------- same instance every time ----------
        System.out.println("eager same instance:  " + (EagerConfig.getInstance() == EagerConfig.getInstance()));
        System.out.println("lazy same instance:   " + (LazyConfig.getInstance() == LazyConfig.getInstance()));
        System.out.println("holder same instance: " + (HolderConfig.getInstance() == HolderConfig.getInstance()));
        System.out.println("enum same instance:   " + (EnumConfig.INSTANCE == EnumConfig.INSTANCE));
        // new EagerConfig();                                      // COMPILE ERROR: constructor is private (outside the class)

        // ---------- 16 threads race to get each singleton: how many objects were built? ----------
        Set<Object> seen = ConcurrentHashMap.newKeySet();
        hammer(() -> {
            seen.add(EagerConfig.getInstance());
            seen.add(LazyConfig.getInstance());
            seen.add(HolderConfig.getInstance());
        }, 16);
        System.out.println("distinct objects seen across 16 racing threads (3 singletons): " + seen.size());
        System.out.println("constructor runs: eager=" + eagerCreated + ", lazy=" + lazyCreated + ", holder=" + holderCreated);

        // ---------- the enum version holds state ----------
        EnumConfig.INSTANCE.setMode("production");
        System.out.println("enum singleton mode (seen from anywhere): " + EnumConfig.INSTANCE.mode());

        // ============================================
        // THE TESTING PROBLEM (why many teams avoid singletons)
        // EnumConfig now remembers "production" for the REST of the program. A test that runs later
        // inherits that state. Tests stop being independent. With dependency injection, each test
        // would pass in its own fresh object.
        // ============================================

        // ============================================
        // WHEN IT MAKES THE CODE WORSE (exit-test material)
        // Using a Singleton just for convenient global access to a "UserService" or "Database" object
        // that many classes call directly: you cannot swap it for a fake, cannot run two versions,
        // and every class secretly depends on it. Pass the object in through the constructor instead.
        // ============================================
    }
}
