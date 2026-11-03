# `_8_DataCenterCloudAndSdn.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Data-center networks connect thousands of servers inside one facility, cloud networks give each customer a virtual private slice of such a network, and software-defined networking (SDN) separates the brains of the network (control plane) from the forwarding hardware (data plane) so it can be programmed centrally. Together they explain how modern web services, clouds and large machine-learning clusters are wired and managed.

**Topologies.** The classic *three-tier* design has access switches (servers attach here), aggregation (or distribution) switches, and core switches. It is good for north-south traffic (users to servers), but server-to-server (east-west) traffic must climb the tree and share *oversubscribed* uplinks. Oversubscription ratio = total downlink bandwidth / total uplink bandwidth of a switch; 2.5:1 means that if everything talks at once each server gets 40 percent of line rate. *Leaf-spine* (a Clos network) has two layers: every leaf switch connects to every spine switch, and servers attach only to leaves. For L leaves and S spines there are L x S fabric links, any two leaves are exactly two switch hops apart, and there are S equal-cost paths between any two leaves; you add spines for bandwidth and leaves for ports, and ECMP (equal-cost multipath) load-balances flows across the spines. The *fat-tree* built from identical k-port switches has k pods, each with k/2 edge and k/2 aggregation switches, (k/2)^2 core switches, supports k^3/4 hosts using 5k^2/4 switches, and has (k/2)^2 equal-cost paths between hosts in different pods.

**AI-training clusters (stated carefully).** Distributed training synchronises gradients between many accelerators, using collective operations such as all-reduce. In a ring all-reduce over N nodes each node sends (and receives) 2(N-1)/N times the data size. Because the step finishes only when the slowest transfer does, such clusters value high bisection bandwidth, low oversubscription and low, predictable latency; they commonly use leaf-spine or fat-tree style fabrics and RDMA transports (InfiniBand or RDMA over Ethernet, RoCE). Actual designs vary by vendor and scale, and the numbers in this file are arithmetic lower bounds, not benchmarks.

**Cloud networking.** A *VPC* (virtual private cloud) is a logically isolated network with a private CIDR block (for example 10.0.0.0/16) that you divide into *subnets*. A *public* subnet has a route to an internet gateway; a *private* subnet does not (it may reach out through a NAT gateway). *Security groups* are stateful allow-lists attached to instances or network interfaces; there is no deny rule and return traffic is automatic. *Network ACLs* are stateless, ordered, per-subnet rules with explicit allow and deny. Some providers reserve addresses in each subnet (AWS reserves 5, so a /24 has 251 usable instead of 254); details are provider-specific.

**Load balancers.** An L4 balancer chooses a backend from IP and port only (fast, protocol-agnostic). An L7 balancer reads the application request, so it can route by URL path, host or cookie, terminate TLS and retry. Algorithms: *round robin* (take turns, ignores load), *least connections* (pick the backend with the fewest active connections, adapts to long requests), weighted variants, and hashing for stickiness. Health checks remove failed backends.

**SDN.** In traditional gear each device runs its own control plane (learning MACs, running routing protocols) and data plane (forwarding). In SDN the devices keep a fast data plane driven by *flow tables*, and a logically centralised *controller* programs them through a southbound API (OpenFlow is the classic one); applications use the controller's northbound API. An OpenFlow-style entry is a *match* on header fields, a *priority*, and an *action* (output port, drop, send to controller), plus counters. A packet matching no entry (*table miss*) is usually sent to the controller (*packet-in*), which can install a rule so later packets are forwarded in hardware.

**Network virtualisation.** A *VLAN* (IEEE 802.1Q) inserts a 4-byte tag (TPID 0x8100, 3-bit priority, 1-bit DEI, 12-bit VLAN ID), giving 4094 usable VLANs because IDs 0 and 4095 are reserved. *VXLAN* (RFC 7348) tunnels Layer-2 frames over a Layer-3 network inside UDP (destination port 4789) with an 8-byte header carrying a 24-bit VNI, giving about 16.7 million segments. It adds 50 bytes of overhead (outer Ethernet 14 + IP 20 + UDP 8 + VXLAN 8), so the underlay MTU is usually raised.

Typical exam questions: compute the number of links/paths in a topology; oversubscription; L4 vs L7 balancing; control vs data plane; what is a flow table entry; why VXLAN instead of VLAN.

## Full Line-by-Line Breakdown

### SECTION 1: THREE-TIER TOPOLOGY AND OVERSUBSCRIPTION
With 2 core, 4 aggregation and 8 access switches and 20 servers per access switch, the link counts are 2 x 4 = 8 core-aggregation links, 8 access switches x 2 uplinks = 16 aggregation-access links, and 160 server links. The access switch has 20 x 10G = 200G down and 2 x 40G = 80G up, so 2.5:1. The numbers are an invented design, not a specific product.

```text
===== SECTION 1: THREE-TIER TOPOLOGY AND OVERSUBSCRIPTION =====
2 core, 4 aggregation, 8 access switches, 20 servers per access switch
links: core-agg = 2x4 = 8, agg-access = 8x2 = 16, server-access = 160; servers = 160
Access switch: 20 x 10G down = 200 G, 2 x 40G up = 80 G -> oversubscription 2.50:1
check: OK (2.5:1 means that if all servers talk at line rate across the tree, each gets 40% of its speed)
Three-tier (access / aggregation / core) suits north-south traffic (clients <-> servers) and uses spanning tree or
routing; east-west server-to-server traffic must climb to the aggregation or core and shares oversubscribed uplinks.
```

### SECTION 2: LEAF-SPINE AND FAT-TREE, VERIFIED BY BFS
The code builds adjacency dictionaries for an 8-leaf, 4-spine fabric and a k = 4 fat-tree. `shortest_paths` runs a breadth-first search that also counts the number of distinct shortest paths. Results confirm the formulas: 32 fabric links and 4 equal-cost paths between leaves (host to host is 4 links), and for the fat-tree 16 hosts, 20 switches, and 4 equal-cost paths of 6 links between hosts in different pods. The ring all-reduce arithmetic gives 1.75 GB per node for 1 GB of data across 8 nodes, which at an assumed 100 Gb/s per node takes at least 0.14 s; it ignores latency and overlap with computation.

```text
===== SECTION 2: LEAF-SPINE AND FAT-TREE, VERIFIED BY BFS =====
Leaf-spine: 8 leaves x 4 spines -> fabric links L*S = 32; hosts = 32
  host on leaf0 -> host on leaf7: 4 links (host-leaf-spine-leaf-host), 4 equal-cost paths (one per spine)
  every leaf pair is exactly 2 switch hops apart; add a spine to add bandwidth without changing hop count. check: OK
  example port plan: leaf with 24 x 25G down, 4 x 100G up -> oversubscription 1.50:1 (1:1 or below = non-blocking)
Fat-tree k=4: hosts k^3/4 = 16 (built 16), switches 5k^2/4 = 20 (built 20),
  hosts in different pods: 6 links, 4 equal-cost paths = (k/2)^2
check: OK (formulas match the graph that was actually built)
-- Relevance to AI-training clusters (stated carefully) --
Ring all-reduce of 1 GB across 8 nodes: each node sends 2(N-1)/N x data = 1.750 GB.
At an assumed 100 Gb/s per node that is >= 0.140 s (bandwidth only, ideal lower bound; ignores latency/overlap).
Why it matters: gradient sync is all-to-all-like and synchronous, so one slow link slows every GPU. Training clusters
therefore tend to use high-bisection, low-oversubscription fabrics (leaf-spine / fat-tree style) with RDMA transports
(InfiniBand or RoCE). Exact designs vary by vendor and scale; this model only shows the arithmetic and the topology idea.
```

### SECTION 3: CLOUD NETWORKING - VPC, SUBNETS, SECURITY GROUPS
`ipaddress` splits 10.0.0.0/16 into /24 subnets (256 of them) and prints the first three with classic (2 fewer) and AWS-style (5 fewer) usable counts. `sg_allows` models an inbound allow-list: anything not matched is implicitly denied. The web group allows HTTPS from anywhere; the database group allows PostgreSQL's port 5432 only from the app subnet.

```text
===== SECTION 3: CLOUD NETWORKING - VPC, SUBNETS, SECURITY GROUPS =====
  public-a       10.0.0.0/24  addresses 256, classic usable 254, AWS-style usable 251 (that provider reserves 5 per subnet)
  private-app-a  10.0.1.0/24  addresses 256, classic usable 254, AWS-style usable 251 (that provider reserves 5 per subnet)
  private-db-a   10.0.2.0/24  addresses 256, classic usable 254, AWS-style usable 251 (that provider reserves 5 per subnet)
VPC 10.0.0.0/16 holds 256 possible /24 subnets. 'Public' = route to an internet gateway; 'private' = no such route.
  security group 'web':  203.0.113.5 -> tcp/443   ALLOW
  security group 'web':  203.0.113.5 -> tcp/22    DENY (implicit)
  security group 'db':    10.0.1.17 -> tcp/5432  ALLOW
  security group 'db':     10.0.0.9 -> tcp/5432  DENY (implicit)
check: OK
Security group = stateful, allow-rules only, attached to an instance/interface (replies are automatically allowed).
Network ACL = stateless, per subnet, ordered rules with explicit allow/deny (return traffic needs its own rule).
TRAP: a security group has no 'deny' rule; to block one address you need a network ACL or firewall. Details are provider-specific.
```

### SECTION 4: LOAD BALANCERS - L4 VS L7, ROUND ROBIN VS LEAST CONNECTIONS
`l7_route` shows content-based routing. `simulate` runs 400 ticks with 2 arrivals per tick and 4 servers; 10 percent of requests are "heavy" (40 ticks of work) and the rest take 2. Both strategies are deterministic (seeded). Round robin gives each server exactly 200 requests but ignores their weight, so a server can accumulate several heavy requests; least-connections sends fewer requests to busy servers and has a lower worst instantaneous load in this run. The workload mix is assumed, so this is an illustration, not a benchmark.

```text
===== SECTION 4: LOAD BALANCERS - L4 VS L7, ROUND ROBIN VS LEAST CONNECTIONS =====
L4 balancer: decides from IP + port (+ protocol); fast, protocol-agnostic, cannot see URLs or cookies.
L7 balancer: reads the request (HTTP path, host, headers, cookies) so it can route /api to one pool and /img to another,
             terminate TLS, retry; costs more CPU.
  l7_route: {'/api/users': 'api-pool', '/img/logo.png': 'static-pool', '/index.html': 'web-pool'}
  round-robin        requests per server [200, 200, 200, 200]; worst instantaneous load on any server = 7
  least-connections  requests per server [186, 245, 200, 169]; worst instantaneous load on any server = 4
check: OK (least-connections peak 4 <= round-robin peak 7 for this seeded workload)
Round robin is blind to how long each request lasts; least-connections adapts. With uniform requests they behave alike.
Result depends on the assumed request mix above, it is a model, not a benchmark.
```

### SECTION 5: SDN - CONTROL PLANE VS DATA PLANE, MATCH-ACTION TABLE
`FlowTable` keeps entries sorted by priority; `lookup` returns the action of the first entry whose match fields all equal the packet's (fields absent from the match are wildcards) and counts hits and misses. The operator pre-installs a priority-100 rule that drops 10.0.0.66. The first web packet misses, `controller_packet_in` installs a rule, and later web packets hit in the data plane. The telnet packet (port 23) misses and the controller installs a drop rule. Final table: 3 entries, 2 misses.

```text
===== SECTION 5: SDN - CONTROL PLANE VS DATA PLANE, MATCH-ACTION TABLE =====
Traditional: each switch/router runs its own control plane (learning, routing protocols) AND data plane (forwarding).
SDN: switches keep only the data plane (flow tables); a logically centralised controller decides the rules and installs
them over a southbound API such as OpenFlow; applications talk to the controller via a northbound API.
   10.0.0.5 -> 10.9.9.9:80  action=output:2  (TABLE MISS -> packet-in to controller, rule installed)
   10.0.0.5 -> 10.9.9.9:80  action=output:2  (hit in data plane)
  10.0.0.66 -> 10.9.9.9:80  action=drop      (hit in data plane)
   10.0.0.5 -> 10.9.9.9:23  action=drop      (TABLE MISS -> packet-in to controller, rule installed)
   10.0.0.7 -> 10.9.9.9:80  action=output:2  (hit in data plane)
  flow table now (3 entries, 2 misses):
    priority 100 match {'src_ip': '10.0.0.66'} -> drop (hits 1)
    priority  10 match {'dst_ip': '10.9.9.9', 'dst_port': 80} -> output:2 (hits 2)
    priority   1 match {'dst_port': 23} -> drop (hits 0)
check: OK (2 misses = first web packet and the telnet packet; the 2nd and 5th packets were forwarded by the table)
Match-action = the same abstraction as a firewall ACL, a router FIB and a switch MAC table: match fields -> action.
TRAP: a controller is a single point of failure/bottleneck if every packet goes to it; hence rules are installed proactively or after one miss.
```

### SECTION 6: NETWORK VIRTUALISATION - VLAN AND VXLAN
`vlan_tag` packs TPID and the TCI (priority shifted 13 bits plus the 12-bit VID) with `struct`; `parse_vlan` reverses it, giving `8100a064` for VLAN 100, priority 5 (0xA064 = 101 0 000001100100). `vxlan_header` packs the flag byte 0x08, three reserved bytes and the VNI shifted left by 8 (24-bit VNI plus a reserved byte): VNI 5001 is 0x001389. The trap: with a 1500-byte underlay IP MTU, 36 bytes of outer IP+UDP+VXLAN plus the 14-byte inner Ethernet header ride inside it, leaving a tenant IP MTU of 1450.

```text
===== SECTION 6: NETWORK VIRTUALISATION - VLAN AND VXLAN =====
802.1Q tag for VLAN 100, priority 5: 8100a064 (4 bytes) -> parsed (TPID, PCP, VID) = (33024, 5, 100)
VID is 12 bits -> 4096 values, VID 0 and 4095 reserved -> 4094 usable VLANs. Tagged frame is 4 bytes bigger (1518 -> 1522).
VXLAN header for VNI 5001: 0800000000138900 (8 bytes) -> parsed VNI = 5001
VNI is 24 bits -> 16,777,216 segments. Carried in UDP (destination port 4789): outer Ethernet 14 + IPv4 20 + UDP 8 + VXLAN 8 = 50 bytes.
TRAP: with a 1500-byte underlay IP MTU, the outer IP+UDP+VXLAN headers (36) and the inner Ethernet header (14) ride inside it,
      so the tenant IP MTU is only 1500 - 50 = 1450. Raise the underlay MTU (jumbo frames) or lower the tenant MTU.
VLAN = L2 segmentation inside one site (4094 IDs). VXLAN = overlay: L2 segments tunnelled over an L3 fabric, which is why it
pairs with leaf-spine and multi-tenant clouds. check: OK
```

## Worked Example
**Q.** A k = 4 fat-tree is built from 4-port switches. How many hosts and switches does it have, and how many equal-cost shortest paths and links join two hosts in different pods?

1. Hosts = k^3 / 4 = 64 / 4 = 16.
2. Switches = 5k^2 / 4 = 5 x 16 / 4 = 20 (8 edge + 8 aggregation + 4 core).
3. Equal-cost paths between hosts in different pods = (k/2)^2 = 4 (one per core switch that connects the two pods' aggregation choices).
4. Path: host - edge - aggregation - core - aggregation - edge - host = 6 links.

The BFS on the graph built by the code confirmed 16, 20, 4 and 6.

## Key Rules / Gotchas Recap
- Leaf-spine: L x S links, S paths, constant 2-switch-hop distance between leaves; fat-tree: k^3/4 hosts, 5k^2/4 switches, (k/2)^2 paths.
- Oversubscription = downlink bandwidth / uplink bandwidth.
- Security group = stateful allow-only; network ACL = stateless ordered allow/deny.
- Round robin ignores load; least-connections adapts to long requests; L7 balancing can see the URL, L4 cannot.
- SDN: controller decides, switches forward; a table miss triggers packet-in; priority resolves overlaps.
- VLAN: 12-bit ID, 4094 usable. VXLAN: 24-bit VNI, UDP 4789, 50 bytes overhead, raise the underlay MTU.
- AI-training fabrics: arithmetic here is a lower bound; real designs differ.

## Why This Matters
Whether you deploy a model behind a load balancer in a VPC or train across a GPU cluster, throughput is often limited by the network topology, oversubscription and MTU rather than by compute. Understanding match-action tables and overlays also makes Kubernetes networking, cloud firewalls and service meshes much less mysterious.
