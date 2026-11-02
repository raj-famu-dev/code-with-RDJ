// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.PriorityQueue;
import java.util.Random;

/**
 * MIN-HEAP (a priority queue). A COMPLETE binary tree stored in a plain int[]:
 *   parent of i = (i - 1) / 2      left child = 2i + 1      right child = 2i + 2
 * Rule: every parent is <= its children, so the SMALLEST element is always at index 0.
 * NO java.util collections inside the heap (java.util.PriorityQueue is only the oracle in main()).
 *
 * Big-O (n = elements):
 *   peek (min)               O(1)
 *   add                      O(log n)   (append at the end, "sift up")
 *   poll (remove min)        O(log n)   (move the last to the root, "sift down")
 *   build from n elements    O(n)       (heapify: NOT O(n log n); a classic interview question)
 *   contains / arbitrary remove   O(n)  (a heap is only ordered parent-to-child, not searchable)
 *   heap sort                O(n log n) time, O(1) extra space
 */
public class _6_MinHeap {

    static class MinHeap {
        private int[] data = new int[8];
        private int size;
        long swaps;                                                // counts swaps so heapify can be measured

        int size() {
            return size;
        }

        boolean isEmpty() {
            return size == 0;
        }

        int peek() {
            if (size == 0) throw new java.util.NoSuchElementException("heap is empty");
            return data[0];
        }

        void add(int value) {
            if (size == data.length) {
                int[] bigger = new int[size * 2];
                System.arraycopy(data, 0, bigger, 0, size);
                data = bigger;
            }
            data[size] = value;                                    // put it in the next free leaf slot...
            siftUp(size);                                          // ...then float it up until the parent is not larger
            size++;
        }

        int poll() {
            if (size == 0) throw new java.util.NoSuchElementException("heap is empty");
            int min = data[0];
            size--;
            data[0] = data[size];                                  // move the LAST element to the root...
            if (size > 0) siftDown(0, size);                       // ...then sink it down to restore the rule
            return min;
        }

        private void siftUp(int i) {
            while (i > 0) {
                int parent = (i - 1) / 2;
                if (data[parent] <= data[i]) break;
                swap(parent, i);
                i = parent;
            }
        }

        private void siftDown(int i, int limit) {
            while (true) {
                int left = 2 * i + 1;
                int right = left + 1;
                int smallest = i;
                if (left < limit && data[left] < data[smallest]) smallest = left;
                if (right < limit && data[right] < data[smallest]) smallest = right;   // pick the SMALLER child
                if (smallest == i) return;
                swap(i, smallest);
                i = smallest;
            }
        }

        private void swap(int a, int b) {
            int tmp = data[a];
            data[a] = data[b];
            data[b] = tmp;
            swaps++;
        }

        // Build a heap from an existing array in O(n): sift down every NON-LEAF node, last to first.
        static MinHeap heapify(int[] values) {
            MinHeap heap = new MinHeap();
            heap.data = new int[Math.max(8, values.length)];
            System.arraycopy(values, 0, heap.data, 0, values.length);
            heap.size = values.length;
            for (int i = heap.size / 2 - 1; i >= 0; i--) {         // nodes from size/2 onward are leaves: already valid heaps
                heap.siftDown(i, heap.size);
            }
            return heap;
        }

        boolean isValidHeap() {
            for (int i = 1; i < size; i++) {
                if (data[(i - 1) / 2] > data[i]) return false;
            }
            return true;
        }

        String layout() {
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < size; i++) sb.append(i > 0 ? " " : "").append(data[i]);
            return sb.append("]").toString();
        }
    }

    // In-place heap sort on a plain array: build a MAX-heap, then repeatedly move the max to the end.
    static void heapSort(int[] a) {
        int n = a.length;
        for (int i = n / 2 - 1; i >= 0; i--) maxSiftDown(a, i, n);
        for (int end = n - 1; end > 0; end--) {
            int tmp = a[0];
            a[0] = a[end];
            a[end] = tmp;                                          // the largest is now in its final place
            maxSiftDown(a, 0, end);
        }
    }

    private static void maxSiftDown(int[] a, int i, int limit) {
        while (true) {
            int left = 2 * i + 1;
            int right = left + 1;
            int largest = i;
            if (left < limit && a[left] > a[largest]) largest = left;
            if (right < limit && a[right] > a[largest]) largest = right;
            if (largest == i) return;
            int tmp = a[i];
            a[i] = a[largest];
            a[largest] = tmp;
            i = largest;
        }
    }

    // Top-k with a SIZE-k heap: keeps the k LARGEST values in O(n log k) time and O(k) space, instead of sorting all n.
    static int[] topK(int[] values, int k) {
        MinHeap heap = new MinHeap();                              // a MIN-heap of the k best so far: the root is the weakest of them
        for (int v : values) {
            if (heap.size() < k) {
                heap.add(v);
            } else if (v > heap.peek()) {
                heap.poll();                                       // evict the weakest
                heap.add(v);
            }
        }
        int[] result = new int[heap.size()];
        for (int i = 0; i < result.length; i++) result[i] = heap.poll();   // comes out ascending
        return result;
    }

    public static void main(String[] args) {

        MinHeap heap = new MinHeap();
        for (int v : new int[]{5, 3, 8, 1, 9, 2}) heap.add(v);
        System.out.println("array layout after adding 5 3 8 1 9 2: " + heap.layout() + "   (index 0 is the minimum, NOT a sorted array)");
        System.out.println("peek = " + heap.peek() + ", size = " + heap.size());
        StringBuilder out = new StringBuilder();
        while (!heap.isEmpty()) out.append(heap.poll()).append(' ');
        System.out.println("polling everything gives sorted order: " + out.toString().trim());
        try {
            heap.poll();
        } catch (java.util.NoSuchElementException e) {
            System.out.println("NoSuchElementException: " + e.getMessage());
        }

        // ---------- heapify is O(n), repeated add is O(n log n): MEASURE it with swap counts ----------
        Random random = new Random(8);
        int n = 100_000;
        int[] values = new int[n];
        for (int i = 0; i < n; i++) values[i] = random.nextInt(1_000_000);
        MinHeap byAdding = new MinHeap();
        for (int v : values) byAdding.add(v);
        MinHeap byHeapify = MinHeap.heapify(values);
        System.out.println("build from " + n + " random values: repeated add = " + byAdding.swaps + " swaps, heapify = " + byHeapify.swaps
                + " swaps (both valid: " + (byAdding.isValidHeap() && byHeapify.isValidHeap()) + ")");

        // ---------- heap sort and top-k ----------
        int[] toSort = {9, 4, 7, 1, 8, 2, 6, 3, 5, 0};
        heapSort(toSort);
        StringBuilder sorted = new StringBuilder();
        for (int v : toSort) sorted.append(v).append(' ');
        System.out.println("heap sort: " + sorted.toString().trim());
        int[] top = topK(new int[]{15, 3, 99, 42, 8, 77, 61, 5, 23, 90}, 3);
        System.out.println("top 3 largest of 15 3 99 42 8 77 61 5 23 90: " + top[0] + " " + top[1] + " " + top[2]);

        // ---------- ORACLE TEST vs java.util.PriorityQueue ----------
        Random r = new Random(404);
        MinHeap ours = new MinHeap();
        PriorityQueue<Integer> oracle = new PriorityQueue<>();
        boolean ok = true;
        for (int step = 0; step < 50_000; step++) {
            if (r.nextInt(3) != 0 || oracle.isEmpty()) {
                int v = r.nextInt(10_000);
                ours.add(v);
                oracle.add(v);
            } else {
                ok &= ours.poll() == oracle.poll();                // int on the left, so the Integer on the right is UNBOXED: a value compare
            }
            ok &= ours.size() == oracle.size();
            if (!oracle.isEmpty()) ok &= ours.peek() == oracle.peek();
        }
        ok &= ours.isValidHeap();
        System.out.println("oracle test: 50000 random operations match java.util.PriorityQueue: " + ok);

        // ============================================
        // THINGS TO BREAK ON PURPOSE
        // 1) In siftDown, compare only against the LEFT child. The heap becomes invalid: write isValidHeap() to catch it.
        // 2) In heapify, loop i from 0 upward instead of size/2 - 1 downward. Does the result stay a valid heap?
        // 3) Flip every comparison (<= to >=) to turn it into a MAX-heap, then use it to solve top-k "smallest".
        // ============================================
    }
}
