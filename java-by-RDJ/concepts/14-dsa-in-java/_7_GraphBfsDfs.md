> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Graphs: BFS and DFS

## Concept

A **graph** is vertices joined by edges (undirected: both ways; directed: one way). It models maps, networks, dependencies, social links. It is stored here as an **adjacency list**: for each vertex, an array of its neighbours, built from plain `int[][]` (no `java.util` collections inside the graph).

Two ways to explore it:

- **BFS** (breadth-first): visit in rings of distance from the start, using a **queue**.
- **DFS** (depth-first): go as deep as possible, then backtrack, using a **stack** (or recursion).

## Big-O (V = vertices, E = edges)

| Item | Time | Space |
|---|---|---|
| adjacency list storage | n/a | **O(V + E)** |
| adjacency **matrix** storage (for comparison) | n/a | **O(V^2)** |
| `addEdge` | **O(1)** amortized | |
| "is there an edge u-v?" | O(degree(u)) (list) / O(1) (matrix) | |
| BFS, DFS | **O(V + E)** | **O(V)** |
| BFS shortest path (unweighted) | **O(V + E)** | O(V) |
| connected components | **O(V + E)** | O(V) |
| cycle detection (undirected) | **O(V + E)** | O(V) |
| topological sort (Kahn's algorithm) | **O(V + E)** | O(V) |

Adjacency lists win when the graph is **sparse** (E much smaller than V^2), which most real graphs are.

## Full Line-by-Line Breakdown

**BFS.** Mark a vertex **seen when it is enqueued**, not when it is dequeued; otherwise the same vertex can be queued many times. The queue is a plain `int[V]` because each vertex enters at most once.

**Shortest path.** BFS reaches each vertex first by the fewest edges (in an unweighted graph), so storing each vertex's `parent` at discovery lets you walk back from the target. This is *not* valid for weighted edges (that needs Dijkstra, which is the heap's job).

**DFS, two versions.** Recursive is shortest; the explicit-stack version pushes neighbours in **reverse** so the first neighbour is explored first, matching the recursive order. The iterative version marks a vertex when it is **popped**, so duplicates on the stack are skipped.

**Connected components.** Start a DFS from every still-unvisited vertex; the number of starts is the number of components.

**Cycle in an undirected graph.** During DFS, meeting an already-seen vertex that is **not the one you just came from** is a back edge, so there is a cycle. Without the `next != parent` check every edge looks like a cycle, because an undirected edge appears in both directions.

**Topological sort (Kahn).** Count each vertex's incoming edges. Repeatedly take a vertex with none, "remove" its outgoing edges, and decrement its neighbours' counts. If fewer than V vertices were processed, a cycle blocked the rest and **no valid order exists**.

The demo graph (an island `6-7` is separate):

```
        0
       / \
      1   2        edges: 0-1, 0-2, 1-3, 1-4, 2-5, 4-5, and 6-7
     / \   \
    3   4---5
```

Real output:

```
BFS from 0:                  0 1 2 3 4 5   (rings: 0 | 1 2 | 3 4 5)
DFS from 0 (recursive):      0 1 3 4 5 2
DFS from 0 (explicit stack): 0 1 3 4 5 2
shortest path 0 -> 5:        0 2 5   (2 edges, found by BFS)
shortest path 3 -> 5:        3 1 4 5
shortest path 0 -> 7:        (none)   (7 is on the other island)
connected components:        2   ({0..5} and {6,7})
has a cycle (1-4-5-2-0-1):   true
has a cycle (a tree):        false
topological order of courses: 0 1 2 3 4
after adding 4 -> 0 (a cycle): null: no valid order exists
path of 1000000 vertices: BFS visited 1000000, iterative DFS visited 1000000
recursive DFS on that path: StackOverflowError (use the explicit stack for deep graphs)
BFS and DFS reach the same vertices: true [0, 1, 2, 3, 4, 5]
```

**The stack-overflow line is environment-dependent.** On this JDK 21 run (default stack size) recursive DFS over a 1,000,000-vertex path threw `StackOverflowError`. The code catches it and prints either outcome, so the program always terminates, but a JVM with a bigger `-Xss` could print the "survived" line instead. The lesson (deep graphs need an explicit stack) does not depend on the exact threshold.

**BFS vs DFS order.** Both visit the same *set* (the last line checks it); only the *order* differs. BFS gives rings, DFS gives a deep path first.

## Key Rules

1. BFS = queue = shortest path in **unweighted** graphs.
2. DFS = stack/recursion = explore everything, detect cycles, topological order.
3. Always keep a `seen` set; without it a cycle loops forever.
4. Mark on **enqueue** for BFS.
5. Recursion depth equals path length: use an explicit stack for deep graphs.

## Gotchas Recap

- Undirected cycle detection needs the parent check; **directed** cycle detection needs a "currently on the stack" marker instead (the `next != parent` trick is wrong for directed graphs, one of the "break on purpose" tasks).
- Disconnected graphs: one traversal reaches only one component.
- Do not print or hash a structure containing a cycle with a naive `toString`.
- Self-loops and duplicate (parallel) edges are not rejected by `addEdge`.

## Why This Structure Exists

Trees are graphs without cycles, so everything before this file was a special case. BFS and DFS underlie routing, dependency resolution (build tools, package managers), web crawling and most "graph" interview questions.
