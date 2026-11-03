// Tags: #Java #DSA #DataStructures #GraphBfsDfs | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.List;

/**
 * GRAPHS: vertices (nodes) joined by edges. Stored as an ADJACENCY LIST: for each vertex, the list of its neighbours.
 * Traversals: BFS (breadth-first, uses a QUEUE) and DFS (depth-first, uses a STACK or recursion).
 * The graph's own storage is built from plain int arrays (no java.util collections inside it).
 * java.util.List / ArrayList appear only to hand back results from the algorithms and in the demo's expected values.
 *
 * Big-O (V = vertices, E = edges):
 *   Adjacency list:  memory O(V + E)    addEdge O(1)    "is there an edge u-v?" O(degree(u))
 *   Adjacency matrix (for comparison):   memory O(V^2)   addEdge O(1)    "is there an edge u-v?" O(1)
 *   BFS, DFS                      O(V + E) time, O(V) extra space
 *   BFS shortest path (UNWEIGHTED) O(V + E)
 *   connected components          O(V + E)
 *   cycle detection (undirected)  O(V + E)
 *   topological sort (DAG, Kahn)  O(V + E)
 */
public class _7_GraphBfsDfs {

    static class Graph {
        private final int vertices;
        private final boolean directed;
        private int[][] adjacency;                                 // adjacency[v] = neighbours of v, in an exactly-sized array
        private final int[] degree;                                // how many slots of adjacency[v] are used
        int edges;

        Graph(int vertices, boolean directed) {
            this.vertices = vertices;
            this.directed = directed;
            this.adjacency = new int[vertices][2];
            this.degree = new int[vertices];
        }

        int vertices() {
            return vertices;
        }

        void addEdge(int from, int to) {
            check(from);
            check(to);
            append(from, to);
            if (!directed) append(to, from);                       // undirected: store the edge in BOTH directions
            edges++;
        }

        private void append(int v, int neighbour) {
            if (degree[v] == adjacency[v].length) {
                int[] bigger = new int[adjacency[v].length * 2];
                System.arraycopy(adjacency[v], 0, bigger, 0, degree[v]);
                adjacency[v] = bigger;
            }
            adjacency[v][degree[v]++] = neighbour;
        }

        private void check(int v) {
            if (v < 0 || v >= vertices) throw new IllegalArgumentException("no such vertex: " + v);
        }

        int degreeOf(int v) {
            return degree[v];
        }

        int neighbour(int v, int i) {
            return adjacency[v][i];
        }
    }

    // ============================================
    // BFS: visit vertices in rings of distance from the start. A QUEUE makes it "first discovered, first explored".
    // ============================================
    static int[] bfsOrder(Graph g, int start) {
        boolean[] seen = new boolean[g.vertices()];               // mark when DISCOVERED (enqueued), not when dequeued
        int[] queue = new int[g.vertices()];                       // each vertex enters at most once, so V slots is enough
        int[] order = new int[g.vertices()];
        int head = 0;
        int tail = 0;
        int count = 0;
        queue[tail++] = start;
        seen[start] = true;
        while (head < tail) {
            int v = queue[head++];
            order[count++] = v;
            for (int i = 0; i < g.degreeOf(v); i++) {
                int next = g.neighbour(v, i);
                if (!seen[next]) {
                    seen[next] = true;
                    queue[tail++] = next;
                }
            }
        }
        return java.util.Arrays.copyOf(order, count);
    }

    // BFS also gives the SHORTEST PATH in an unweighted graph: the first time we reach a vertex is via the fewest edges.
    static int[] shortestPath(Graph g, int from, int to) {
        int[] parent = new int[g.vertices()];
        java.util.Arrays.fill(parent, -1);
        boolean[] seen = new boolean[g.vertices()];
        int[] queue = new int[g.vertices()];
        int head = 0;
        int tail = 0;
        queue[tail++] = from;
        seen[from] = true;
        while (head < tail) {
            int v = queue[head++];
            if (v == to) break;
            for (int i = 0; i < g.degreeOf(v); i++) {
                int next = g.neighbour(v, i);
                if (!seen[next]) {
                    seen[next] = true;
                    parent[next] = v;                              // remember how we got here
                    queue[tail++] = next;
                }
            }
        }
        if (!seen[to]) return new int[0];                          // unreachable
        int length = 1;
        for (int v = to; v != from; v = parent[v]) length++;
        int[] path = new int[length];
        int v = to;
        for (int i = length - 1; i >= 0; i--) {                    // walk back from the target, filling from the end
            path[i] = v;
            v = parent[v];
        }
        return path;
    }

    // ============================================
    // DFS: go as deep as possible, then backtrack. Recursive version (short) and explicit-stack version (no StackOverflow).
    // ============================================
    static int[] dfsOrderRecursive(Graph g, int start) {
        boolean[] seen = new boolean[g.vertices()];
        int[] order = new int[g.vertices()];
        int[] count = {0};
        dfs(g, start, seen, order, count);
        return java.util.Arrays.copyOf(order, count[0]);
    }

    private static void dfs(Graph g, int v, boolean[] seen, int[] order, int[] count) {
        seen[v] = true;
        order[count[0]++] = v;
        for (int i = 0; i < g.degreeOf(v); i++) {
            int next = g.neighbour(v, i);
            if (!seen[next]) dfs(g, next, seen, order, count);
        }
    }

    // Same traversal with an explicit stack. Neighbours are pushed in REVERSE so the first neighbour is explored first,
    // which gives the same order as the recursive version.
    static int[] dfsOrderIterative(Graph g, int start) {
        boolean[] seen = new boolean[g.vertices()];
        int[] stack = new int[g.vertices() + g.edges * 2 + 1];     // a vertex can be pushed once per incoming edge
        int top = 0;
        int[] order = new int[g.vertices()];
        int count = 0;
        stack[top++] = start;
        while (top > 0) {
            int v = stack[--top];
            if (seen[v]) continue;                                 // marked when POPPED here, so duplicates are skipped
            seen[v] = true;
            order[count++] = v;
            for (int i = g.degreeOf(v) - 1; i >= 0; i--) {
                int next = g.neighbour(v, i);
                if (!seen[next]) stack[top++] = next;
            }
        }
        return java.util.Arrays.copyOf(order, count);
    }

    // Number of connected components (undirected graph): start a DFS from every still-unvisited vertex.
    static int connectedComponents(Graph g) {
        boolean[] seen = new boolean[g.vertices()];
        int components = 0;
        for (int v = 0; v < g.vertices(); v++) {
            if (!seen[v]) {
                components++;
                int[] order = new int[g.vertices()];
                markAll(g, v, seen, order, new int[]{0});
            }
        }
        return components;
    }

    private static void markAll(Graph g, int v, boolean[] seen, int[] order, int[] count) {
        dfs(g, v, seen, order, count);
    }

    // Cycle in an UNDIRECTED graph: DFS meets an already-seen vertex that is not the one we just came from.
    static boolean hasCycleUndirected(Graph g) {
        boolean[] seen = new boolean[g.vertices()];
        for (int v = 0; v < g.vertices(); v++) {
            if (!seen[v] && cycleFrom(g, v, -1, seen)) return true;
        }
        return false;
    }

    private static boolean cycleFrom(Graph g, int v, int parent, boolean[] seen) {
        seen[v] = true;
        for (int i = 0; i < g.degreeOf(v); i++) {
            int next = g.neighbour(v, i);
            if (!seen[next]) {
                if (cycleFrom(g, next, v, seen)) return true;
            } else if (next != parent) {
                return true;                                       // a back edge
            }
        }
        return false;
    }

    // Topological sort of a DAG (Kahn's algorithm): repeatedly take a vertex with no remaining prerequisites.
    // Returns null if the graph has a cycle (no valid order exists).
    static int[] topologicalSort(Graph g) {
        int[] inDegree = new int[g.vertices()];
        for (int v = 0; v < g.vertices(); v++) {
            for (int i = 0; i < g.degreeOf(v); i++) inDegree[g.neighbour(v, i)]++;
        }
        int[] queue = new int[g.vertices()];
        int head = 0;
        int tail = 0;
        for (int v = 0; v < g.vertices(); v++) {
            if (inDegree[v] == 0) queue[tail++] = v;
        }
        while (head < tail) {
            int v = queue[head++];
            for (int i = 0; i < g.degreeOf(v); i++) {
                int next = g.neighbour(v, i);
                if (--inDegree[next] == 0) queue[tail++] = next;
            }
        }
        return tail == g.vertices() ? queue : null;                // fewer than V processed means a cycle blocked some vertices
    }

    static String show(int[] a) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < a.length; i++) sb.append(i > 0 ? " " : "").append(a[i]);
        return a.length == 0 ? "(none)" : sb.toString();
    }

    public static void main(String[] args) {

        //        0
        //       / \
        //      1   2        0-1, 0-2, 1-3, 1-4, 2-5, 4-5, plus 6-7 as a separate island
        //     / \   \
        //    3   4---5
        Graph g = new Graph(8, false);
        int[][] edges = {{0, 1}, {0, 2}, {1, 3}, {1, 4}, {2, 5}, {4, 5}, {6, 7}};
        for (int[] e : edges) g.addEdge(e[0], e[1]);

        System.out.println("BFS from 0:                  " + show(bfsOrder(g, 0)) + "   (rings: 0 | 1 2 | 3 4 5)");
        System.out.println("DFS from 0 (recursive):      " + show(dfsOrderRecursive(g, 0)));
        System.out.println("DFS from 0 (explicit stack): " + show(dfsOrderIterative(g, 0)));
        System.out.println("shortest path 0 -> 5:        " + show(shortestPath(g, 0, 5)) + "   (2 edges, found by BFS)");
        System.out.println("shortest path 3 -> 5:        " + show(shortestPath(g, 3, 5)));
        System.out.println("shortest path 0 -> 7:        " + show(shortestPath(g, 0, 7)) + "   (7 is on the other island)");
        System.out.println("connected components:        " + connectedComponents(g) + "   ({0..5} and {6,7})");
        System.out.println("has a cycle (1-4-5-2-0-1):   " + hasCycleUndirected(g));

        Graph tree = new Graph(5, false);
        int[][] treeEdges = {{0, 1}, {0, 2}, {2, 3}, {2, 4}};
        for (int[] e : treeEdges) tree.addEdge(e[0], e[1]);
        System.out.println("has a cycle (a tree):        " + hasCycleUndirected(tree));

        // ---------- a DIRECTED graph: course prerequisites ----------
        // 0 Intro -> 1 Data Structures -> 3 Algorithms -> 4 AI ;  0 -> 2 Discrete Math -> 3 ;  2 -> 4
        Graph courses = new Graph(5, true);
        int[][] prerequisites = {{0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 4}, {2, 4}};
        for (int[] e : prerequisites) courses.addEdge(e[0], e[1]);
        System.out.println("topological order of courses: " + show(topologicalSort(courses)));
        courses.addEdge(4, 0);                                     // now AI is a prerequisite of Intro: impossible
        System.out.println("after adding 4 -> 0 (a cycle): " + (topologicalSort(courses) == null ? "null: no valid order exists" : "unexpected"));

        // ---------- scale: a 1,000,000-vertex path graph. Recursive DFS would overflow the stack; BFS and iterative DFS do not ----------
        int big = 1_000_000;
        Graph path = new Graph(big, false);
        for (int i = 0; i + 1 < big; i++) path.addEdge(i, i + 1);
        System.out.println("path of " + big + " vertices: BFS visited " + bfsOrder(path, 0).length
                + ", iterative DFS visited " + dfsOrderIterative(path, 0).length);
        try {
            dfsOrderRecursive(path, 0);
            System.out.println("recursive DFS survived (the default stack happened to be big enough here)");
        } catch (StackOverflowError e) {
            System.out.println("recursive DFS on that path: StackOverflowError (use the explicit stack for deep graphs)");
        }

        // ---------- cross-check: BFS and DFS must reach exactly the same SET of vertices ----------
        List<Integer> bfsSet = new ArrayList<>();
        for (int v : bfsOrder(g, 0)) bfsSet.add(v);
        List<Integer> dfsSet = new ArrayList<>();
        for (int v : dfsOrderRecursive(g, 0)) dfsSet.add(v);
        java.util.Collections.sort(bfsSet);
        java.util.Collections.sort(dfsSet);
        System.out.println("BFS and DFS reach the same vertices: " + bfsSet.equals(dfsSet) + " " + bfsSet);

        // ============================================
        // THINGS TO BREAK ON PURPOSE
        // 1) In bfsOrder: mark `seen` when DEQUEUING instead of when enqueuing. Count how often a vertex enters the queue.
        // 2) In hasCycleUndirected: delete the `next != parent` test. Every graph with an edge "has a cycle". Why?
        // 3) Make the graph directed and run hasCycleUndirected on a DAG that has a diamond (0->1, 0->2, 1->3, 2->3).
        // ============================================
    }
}
