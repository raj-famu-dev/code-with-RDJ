# `_2_NetworkTopologies.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A network topology is the arrangement of devices and links. The *physical* topology is how cables and devices are really laid out; the *logical* topology is how data flows (a physical star with a hub can behave as a logical bus). Topology decides cost, how easily the network grows, and what happens when something breaks.

**The six topologies.**

| Topology | Layout | Cables for n nodes | Advantages | Disadvantages |
|----------|--------|--------------------|------------|---------------|
| Bus | all nodes tap one shared backbone cable, terminated at both ends | 1 backbone + n drop lines | cheap, little cable, easy to install | backbone fault stops everyone; collisions; limited length and nodes; hard to troubleshoot |
| Star | every node cabled to a central hub or switch | n | easy to add or remove nodes, one cable fault affects one node, easy to find faults | the central device is a single point of failure; needs more cable than a bus |
| Ring | each node connected to exactly two neighbours, forming a closed loop | n | orderly access (token passing), no collisions, equal access | one break stops a unidirectional ring; adding a node disrupts the ring; dual ring fixes this |
| Mesh | every node linked directly to every other node | n(n-1)/2 | no traffic sharing, very robust, private links | enormous cabling and n-1 ports per node; costly |
| Tree | hierarchy of stars: a root with branches | n-1 links between n nodes | scalable, easy to manage in groups | root or upper-level failure splits the network; more cabling |
| Hybrid | a combination such as star-of-stars or star-bus | depends | flexible, takes the best of each | complex design, expensive |

**Formulas to memorise.**
- Full mesh links: `n(n-1)/2`. Ports (NICs) per node: `n-1`. Total ports: `n(n-1)`. Note that `n(n-1)` counts each cable twice, once from each end; this is the classic exam trap. `n(n-1)` would only be the right link count if every direction (simplex) were a separate link; for ordinary duplex cables it is `n(n-1)/2`.
- Star: `n` cables, one hub or switch with `n` ports.
- Ring: `n` links for `n` nodes. Bus: `n` drop lines plus one backbone.
- Tree with n nodes: `n-1` links (any tree). A complete binary tree of depth d has `2^(d+1) - 1` nodes.

**Failure behaviour.** Bus: a backbone break splits it in two and breaks signal termination; star: only the cut node is lost unless the hub dies; ring: one break kills a one-way ring but a bidirectional or dual ring heals itself; mesh: survives many failures because many alternative paths exist.

**Typical exam questions.** Compare bus/star/ring/mesh; compute the number of cables and ports for n devices in a mesh; state the effect of a link or hub failure; name the topology of Ethernet (physical star, logical bus when a hub is used); which topology gives the best fault tolerance (mesh).

## Full Line-by-Line Breakdown

### SECTION 1: BUILD EACH TOPOLOGY AS A GRAPH
Every topology becomes a list of edges `(a, b)`; devices are vertices. `star` joins each node to `HUB`; `ring` joins node i to node i+1 and the last to the first (`% n`); `mesh` uses `itertools.combinations` to generate every unordered pair; `bus` models one backbone as tap points joined in a line, with a drop line from each node; `tree` generates children recursively level by level; `hybrid` joins two stars by a trunk between their hubs. The printed counts are *graph edges*; the note explains that bus edges include several pieces of the one backbone cable.

```text
===== SECTION 1: BUILD EACH TOPOLOGY AS A GRAPH =====
star n=5      vertices= 6 graph edges= 5
ring n=5      vertices= 5 graph edges= 5
mesh n=5      vertices= 5 graph edges=10
bus n=5       vertices=10 graph edges= 9
tree depth=2  vertices= 7 graph edges= 6
hybrid        vertices= 8 graph edges= 7
(bus: 5 edges are drop lines, 4 are pieces of the single backbone cable, so 9 edges = 1 physical backbone + 5 drops)
```

### SECTION 2: LINK / PORT COUNTS FOR n NODES
The loop confirms with `assert` that the formula `n(n-1)/2` equals the number of pairs actually generated, while star and ring have exactly n links. Look at how mesh grows: 20 nodes need 190 cables and 19 ports in every machine, while the star needs 20 cables. The trap line shows `n(n-1)` double counting.

```text
===== SECTION 2: LINK / PORT COUNTS FOR n NODES =====
  n   star   ring  bus drops  mesh n(n-1)/2  ports/node (mesh)
  3      3      3          3              3                  2
  4      4      4          4              6                  3
  5      5      5          5             10                  4
  6      6      6          6             15                  5
 10     10     10         10             45                  9
 20     20     20         20            190                 19
Mesh needs n(n-1)/2 cables and n-1 NIC ports on EVERY node; that is why full mesh is rare.
bus: 1 backbone cable + n drop lines (and 2 terminators); star: n cables + 1 hub port each.
Trap: n(n-1) for n=5 gives 20 (counts each cable twice); correct is 10.
check: OK
```

### SECTION 3: FAILURE IMPACT
`components()` removes dead nodes and dead links, then runs a breadth-first search (BFS) from every unvisited vertex to find groups that can still reach each other. One group means the network is still connected; several groups are "islands". Results: a dead hub isolates all five leaves; a dead leaf is harmless; a backbone cut splits the bus 4/6 (tap and node vertices counted); a bidirectional ring survives one cut but two cuts split it; the mesh survives losing three of one node's four cables; losing the tree's root leaves two subtrees; cutting the hybrid's trunk gives two stars.

```text
===== SECTION 3: FAILURE IMPACT =====
star: hub dies                               -> SPLIT into 5 islands [1, 1, 1, 1, 1]
star: one leaf dies                          -> still connected
bus: backbone break between T2-T3            -> SPLIT into 2 islands [4, 6]
bus: one node (N3) dies                      -> still connected
ring (bidirectional): one cable cut          -> still connected
ring: two cables cut                         -> SPLIT into 2 islands [2, 3]
mesh n=5: 3 of the 4 cables at N1 cut        -> still connected
tree: root dies (depth 2)                    -> SPLIT into 2 islands [3, 3]
hybrid: link H1-H2 cut                       -> SPLIT into 2 islands [4, 4]
Trap: a token ring that passes data one way only dies on ONE cut; a dual/bidirectional ring survives it.
```

### SECTION 4: COMPARISON TABLE
A printed summary of advantages, disadvantages and cable counts that you can reproduce in an exam answer.

```text
===== SECTION 4: COMPARISON TABLE =====
topology  advantage                             disadvantage                            cables
bus       cheap, little cable                   backbone fault kills all; collisions    n drops + 1 backbone
star      easy to add/remove, 1 fault isolated  hub is single point of failure          n
ring      orderly access, no collisions         one break stops a unidirectional ring   n
mesh      most reliable, private links          huge cabling and ports                  n(n-1)/2
tree      hierarchical, scalable                root failure splits network             n-1 (nodes)
hybrid    mix of strengths, flexible            complex and costly                      depends
```

### SECTION 5: WORKED EXAMPLE
Arithmetic for the example below.

```text
===== SECTION 5: WORKED EXAMPLE =====
A lab has n=8 computers. Fully meshed: cables = 8*7/2 = 28; ports per PC = 7.
Star: cables = 8; ports per PC = 1; switch ports = 8.
Extra cables for mesh over star = 20.
check: OK
```

## Worked Example
**Problem.** A lab has 8 computers. How many cables and ports does a full mesh need, and how many more cables than a star?

1. Mesh cables = n(n-1)/2 = 8 x 7 / 2 = 28.
2. Each computer needs n-1 = 7 ports.
3. Star cables = 8, one port per computer, plus a switch with 8 ports.
4. Extra cables = 28 - 8 = 20.

The code prints 28, 7, 8 and 20 and asserts them.

## Key Rules / Gotchas Recap
- Full mesh links = n(n-1)/2, not n(n-1).
- Every mesh node needs n-1 ports; cost explodes quadratically.
- Star: hub failure is fatal, leaf failure is local.
- Bus: backbone break splits the network; needs terminators at both ends.
- Unidirectional ring: one cut stops everything; bidirectional/dual ring survives one cut.
- Tree = star of stars; losing the root partitions the network.
- Physical topology and logical topology can differ.

## Why This Matters
Data-centre fabrics, cloud VPC design and Kubernetes cluster networking are all choices about links, hubs and redundancy. The failure analysis here (connected components after a fault) is the same idea used to reason about single points of failure and attack surface.
