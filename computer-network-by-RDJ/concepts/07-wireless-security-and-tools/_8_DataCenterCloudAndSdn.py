# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Data-center, cloud and SDN networking: three-tier vs leaf-spine vs fat-tree
topologies with link/path counts verified by graph search, cloud VPC subnets and
security groups, L4 vs L7 load balancing with a round-robin vs least-connections
simulation, an OpenFlow-style match-action table, and VLAN/VXLAN headers built
with struct. Everything is an in-memory model with seeded randomness."""
import ipaddress
import random
import struct
from collections import deque

# ===== SECTION 1: THREE-TIER TOPOLOGY AND OVERSUBSCRIPTION =====
print("===== SECTION 1: THREE-TIER TOPOLOGY AND OVERSUBSCRIPTION =====")
CORE, AGG, ACCESS, SERVERS_PER_ACCESS = 2, 4, 8, 20
links_core_agg = CORE * AGG                 # every core to every aggregation switch
links_agg_access = ACCESS * 2               # each access switch dual-homed to 2 aggregation switches
links_server = ACCESS * SERVERS_PER_ACCESS
print(f"{CORE} core, {AGG} aggregation, {ACCESS} access switches, {SERVERS_PER_ACCESS} servers per access switch")
print(f"links: core-agg = {CORE}x{AGG} = {links_core_agg}, agg-access = {ACCESS}x2 = {links_agg_access}, "
      f"server-access = {links_server}; servers = {links_server}")
down_gbps, up_gbps = SERVERS_PER_ACCESS * 10, 2 * 40
print(f"Access switch: {SERVERS_PER_ACCESS} x 10G down = {down_gbps} G, 2 x 40G up = {up_gbps} G "
      f"-> oversubscription {down_gbps / up_gbps:.2f}:1")
assert down_gbps / up_gbps == 2.5
print("check: OK (2.5:1 means that if all servers talk at line rate across the tree, each gets 40% of its speed)")
print("Three-tier (access / aggregation / core) suits north-south traffic (clients <-> servers) and uses spanning tree or")
print("routing; east-west server-to-server traffic must climb to the aggregation or core and shares oversubscribed uplinks.")

# ===== SECTION 2: LEAF-SPINE AND FAT-TREE, VERIFIED BY BFS =====
print("\n===== SECTION 2: LEAF-SPINE AND FAT-TREE, VERIFIED BY BFS =====")


def shortest_paths(adj: dict[str, set[str]], a: str, b: str) -> tuple[int, int]:
    """Return (hops, number of distinct shortest paths) using BFS with path counting."""
    dist, count = {a: 0}, {a: 1}
    q = deque([a])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v], count[v] = dist[u] + 1, count[u]
                q.append(v)
            elif dist[v] == dist[u] + 1:
                count[v] += count[u]
    return dist[b], count[b]


def add_edge(adj: dict[str, set[str]], u: str, v: str) -> None:
    adj.setdefault(u, set()).add(v)
    adj.setdefault(v, set()).add(u)


L, S, HOSTS_PER_LEAF = 8, 4, 4
leaf_spine: dict[str, set[str]] = {}
for li in range(L):
    for si in range(S):
        add_edge(leaf_spine, f"leaf{li}", f"spine{si}")
    for h in range(HOSTS_PER_LEAF):
        add_edge(leaf_spine, f"leaf{li}", f"h{li}.{h}")
fabric_links = L * S
hops, npaths = shortest_paths(leaf_spine, "h0.0", "h7.0")
print(f"Leaf-spine: {L} leaves x {S} spines -> fabric links L*S = {fabric_links}; hosts = {L * HOSTS_PER_LEAF}")
print(f"  host on leaf0 -> host on leaf7: {hops} links (host-leaf-spine-leaf-host), {npaths} equal-cost paths (one per spine)")
assert (fabric_links, hops, npaths) == (32, 4, S)
print("  every leaf pair is exactly 2 switch hops apart; add a spine to add bandwidth without changing hop count. check: OK")
leaf_up, leaf_down = 4 * 100, 24 * 25
print(f"  example port plan: leaf with 24 x 25G down, 4 x 100G up -> oversubscription {leaf_down / leaf_up:.2f}:1 (1:1 or below = non-blocking)")

K = 4   # fat-tree built from identical k-port switches
fat: dict[str, set[str]] = {}
half = K // 2
for pod in range(K):
    for e in range(half):
        for a in range(half):
            add_edge(fat, f"edge{pod}.{e}", f"aggr{pod}.{a}")
        for h in range(half):
            add_edge(fat, f"edge{pod}.{e}", f"host{pod}.{e}.{h}")
    for a in range(half):
        for c in range(half):
            add_edge(fat, f"aggr{pod}.{a}", f"core{a}.{c}")
n_hosts = sum(1 for n in fat if n.startswith("host"))
n_sw = sum(1 for n in fat if not n.startswith("host"))
hops_f, paths_f = shortest_paths(fat, "host0.0.0", "host3.1.1")
print(f"Fat-tree k={K}: hosts k^3/4 = {K ** 3 // 4} (built {n_hosts}), switches 5k^2/4 = {5 * K * K // 4} (built {n_sw}),")
print(f"  hosts in different pods: {hops_f} links, {paths_f} equal-cost paths = (k/2)^2")
assert (n_hosts, n_sw, hops_f, paths_f) == (16, 20, 6, 4)
print("check: OK (formulas match the graph that was actually built)")

print("-- Relevance to AI-training clusters (stated carefully) --")
N_NODES, GB = 8, 1.0
traffic = 2 * (N_NODES - 1) / N_NODES * GB
gbit_s = 100
t_ideal = traffic * 8 / gbit_s
print(f"Ring all-reduce of {GB:g} GB across {N_NODES} nodes: each node sends 2(N-1)/N x data = {traffic:.3f} GB.")
print(f"At an assumed {gbit_s} Gb/s per node that is >= {t_ideal:.3f} s (bandwidth only, ideal lower bound; ignores latency/overlap).")
assert abs(traffic - 1.75) < 1e-9
print("Why it matters: gradient sync is all-to-all-like and synchronous, so one slow link slows every GPU. Training clusters")
print("therefore tend to use high-bisection, low-oversubscription fabrics (leaf-spine / fat-tree style) with RDMA transports")
print("(InfiniBand or RoCE). Exact designs vary by vendor and scale; this model only shows the arithmetic and the topology idea.")

# ===== SECTION 3: CLOUD NETWORKING - VPC, SUBNETS, SECURITY GROUPS =====
print("\n===== SECTION 3: CLOUD NETWORKING - VPC, SUBNETS, SECURITY GROUPS =====")
vpc = ipaddress.ip_network("10.0.0.0/16")
subnets = list(vpc.subnets(new_prefix=24))[:3]
names = ["public-a", "private-app-a", "private-db-a"]
for n, s in zip(names, subnets):
    print(f"  {n:<14} {s}  addresses {s.num_addresses}, classic usable {s.num_addresses - 2}, "
          f"AWS-style usable {s.num_addresses - 5} (that provider reserves 5 per subnet)")
assert subnets[0] == ipaddress.ip_network("10.0.0.0/24")
print(f"VPC {vpc} holds {len(list(vpc.subnets(new_prefix=24)))} possible /24 subnets. 'Public' = route to an internet gateway; 'private' = no such route.")

SG_DB = [("tcp", 5432, "10.0.1.0/24")]           # inbound allow-list; nothing else is allowed in
SG_WEB = [("tcp", 443, "0.0.0.0/0")]


def sg_allows(rules: list[tuple[str, int, str]], proto: str, port: int, src: str) -> bool:
    return any(p == proto and pt == port and ipaddress.ip_address(src) in ipaddress.ip_network(cidr)
               for p, pt, cidr in rules)


tests = [("web", SG_WEB, "tcp", 443, "203.0.113.5", True), ("web", SG_WEB, "tcp", 22, "203.0.113.5", False),
         ("db", SG_DB, "tcp", 5432, "10.0.1.17", True), ("db", SG_DB, "tcp", 5432, "10.0.0.9", False)]
for who, rules, proto, port, src, want in tests:
    res = sg_allows(rules, proto, port, src)
    assert res == want
    print(f"  security group '{who}': {src:>12} -> {proto}/{port:<5} {'ALLOW' if res else 'DENY (implicit)'}")
print("check: OK")
print("Security group = stateful, allow-rules only, attached to an instance/interface (replies are automatically allowed).")
print("Network ACL = stateless, per subnet, ordered rules with explicit allow/deny (return traffic needs its own rule).")
print("TRAP: a security group has no 'deny' rule; to block one address you need a network ACL or firewall. Details are provider-specific.")

# ===== SECTION 4: LOAD BALANCERS - L4 VS L7, ROUND ROBIN VS LEAST CONNECTIONS =====
print("\n===== SECTION 4: LOAD BALANCERS - L4 VS L7, ROUND ROBIN VS LEAST CONNECTIONS =====")
print("L4 balancer: decides from IP + port (+ protocol); fast, protocol-agnostic, cannot see URLs or cookies.")
print("L7 balancer: reads the request (HTTP path, host, headers, cookies) so it can route /api to one pool and /img to another,")
print("             terminate TLS, retry; costs more CPU.")


def l7_route(path: str) -> str:
    return "api-pool" if path.startswith("/api") else "static-pool" if path.startswith("/img") else "web-pool"


print("  l7_route:", {p: l7_route(p) for p in ("/api/users", "/img/logo.png", "/index.html")})


def simulate(strategy: str, seed: int = 11, servers: int = 4, ticks: int = 400) -> tuple[list[int], int]:
    rng = random.Random(seed)
    active: list[list[int]] = [[] for _ in range(servers)]    # remaining service time of each running request
    served = [0] * servers
    peak, rr = 0, 0
    for _ in range(ticks):
        for lst in active:
            lst[:] = [t - 1 for t in lst if t - 1 > 0]
        for _ in range(2):                                    # 2 new requests per tick
            duration = 40 if rng.random() < 0.1 else 2        # 10% of requests are 'heavy' (assumed mix)
            if strategy == "round-robin":
                idx, rr = rr % servers, rr + 1
            else:
                idx = min(range(servers), key=lambda i: len(active[i]))
            active[idx].append(duration)
            served[idx] += 1
        peak = max(peak, max(len(a) for a in active))
    return served, peak


for strat in ("round-robin", "least-connections"):
    served, peak = simulate(strat)
    print(f"  {strat:<18} requests per server {served}; worst instantaneous load on any server = {peak}")
rr_peak, lc_peak = simulate("round-robin")[1], simulate("least-connections")[1]
assert lc_peak <= rr_peak
print(f"check: OK (least-connections peak {lc_peak} <= round-robin peak {rr_peak} for this seeded workload)")
print("Round robin is blind to how long each request lasts; least-connections adapts. With uniform requests they behave alike.")
print("Result depends on the assumed request mix above, it is a model, not a benchmark.")

# ===== SECTION 5: SDN - CONTROL PLANE VS DATA PLANE, MATCH-ACTION TABLE =====
print("\n===== SECTION 5: SDN - CONTROL PLANE VS DATA PLANE, MATCH-ACTION TABLE =====")
print("Traditional: each switch/router runs its own control plane (learning, routing protocols) AND data plane (forwarding).")
print("SDN: switches keep only the data plane (flow tables); a logically centralised controller decides the rules and installs")
print("them over a southbound API such as OpenFlow; applications talk to the controller via a northbound API.")


class FlowTable:
    def __init__(self) -> None:
        self.entries: list[dict] = []
        self.misses = 0

    def install(self, priority: int, match: dict, action: str) -> None:
        self.entries.append({"priority": priority, "match": match, "action": action, "hits": 0})
        self.entries.sort(key=lambda e: -e["priority"])        # highest priority first

    def lookup(self, pkt: dict) -> str | None:
        for e in self.entries:
            if all(pkt.get(k) == v for k, v in e["match"].items()):   # missing field in match = wildcard
                e["hits"] += 1
                return e["action"]
        self.misses += 1
        return None


def controller_packet_in(table: FlowTable, pkt: dict) -> str:
    """Controller policy: web traffic out port 2, everything else dropped; installs a rule so later packets stay in the data plane."""
    if pkt["dst_port"] == 80:
        table.install(10, {"dst_ip": pkt["dst_ip"], "dst_port": 80}, "output:2")
        return "output:2"
    table.install(1, {"dst_port": pkt["dst_port"]}, "drop")
    return "drop"


sw = FlowTable()
sw.install(100, {"src_ip": "10.0.0.66"}, "drop")              # operator rule: block one host
stream = [dict(src_ip="10.0.0.5", dst_ip="10.9.9.9", dst_port=80), dict(src_ip="10.0.0.5", dst_ip="10.9.9.9", dst_port=80),
          dict(src_ip="10.0.0.66", dst_ip="10.9.9.9", dst_port=80), dict(src_ip="10.0.0.5", dst_ip="10.9.9.9", dst_port=23),
          dict(src_ip="10.0.0.7", dst_ip="10.9.9.9", dst_port=80)]
for pkt in stream:
    act = sw.lookup(pkt)
    note = "hit in data plane"
    if act is None:
        act = controller_packet_in(sw, pkt)
        note = "TABLE MISS -> packet-in to controller, rule installed"
    print(f"  {pkt['src_ip']:>9} -> {pkt['dst_ip']}:{pkt['dst_port']:<3} action={act:<9} ({note})")
print(f"  flow table now ({len(sw.entries)} entries, {sw.misses} misses):")
for e in sw.entries:
    print(f"    priority {e['priority']:>3} match {e['match']} -> {e['action']} (hits {e['hits']})")
assert sw.misses == 2 and len(sw.entries) == 3
print("check: OK (2 misses = first web packet and the telnet packet; the 2nd and 5th packets were forwarded by the table)")
print("Match-action = the same abstraction as a firewall ACL, a router FIB and a switch MAC table: match fields -> action.")
print("TRAP: a controller is a single point of failure/bottleneck if every packet goes to it; hence rules are installed proactively or after one miss.")

# ===== SECTION 6: NETWORK VIRTUALISATION - VLAN AND VXLAN =====
print("\n===== SECTION 6: NETWORK VIRTUALISATION - VLAN AND VXLAN =====")
TPID = 0x8100


def vlan_tag(vid: int, pcp: int = 0) -> bytes:
    assert 0 <= vid < 4096
    return struct.pack("!HH", TPID, (pcp << 13) | vid)        # 3-bit priority, 1-bit DEI = 0, 12-bit VLAN ID


def parse_vlan(tag: bytes) -> tuple[int, int, int]:
    tpid, tci = struct.unpack("!HH", tag)
    return tpid, tci >> 13, tci & 0x0FFF


tag = vlan_tag(100, pcp=5)
print(f"802.1Q tag for VLAN 100, priority 5: {tag.hex()} (4 bytes) -> parsed (TPID, PCP, VID) = {parse_vlan(tag)}")
assert parse_vlan(tag) == (0x8100, 5, 100)
print(f"VID is 12 bits -> 4096 values, VID 0 and 4095 reserved -> 4094 usable VLANs. Tagged frame is 4 bytes bigger (1518 -> 1522).")


def vxlan_header(vni: int) -> bytes:
    assert 0 <= vni < 2 ** 24
    return struct.pack("!B3xI", 0x08, vni << 8)               # flags (I bit), 3 reserved bytes, 24-bit VNI, 1 reserved byte


def parse_vxlan(h: bytes) -> int:
    flags, word = struct.unpack("!B3xI", h)
    assert flags & 0x08, "VNI flag not set"
    return word >> 8


vx = vxlan_header(5001)
print(f"VXLAN header for VNI 5001: {vx.hex()} (8 bytes) -> parsed VNI = {parse_vxlan(vx)}")
assert parse_vxlan(vx) == 5001 and len(vx) == 8
overhead = 14 + 20 + 8 + 8
print(f"VNI is 24 bits -> {2 ** 24:,} segments. Carried in UDP (destination port 4789): outer Ethernet 14 + IPv4 20 + UDP 8 + VXLAN 8 = {overhead} bytes.")
inner_ip_mtu = 1500 - (20 + 8 + 8 + 14)
print(f"TRAP: with a 1500-byte underlay IP MTU, the outer IP+UDP+VXLAN headers (36) and the inner Ethernet header (14) ride inside it,")
print(f"      so the tenant IP MTU is only 1500 - 50 = {inner_ip_mtu}. Raise the underlay MTU (jumbo frames) or lower the tenant MTU.")
assert inner_ip_mtu == 1450
print("VLAN = L2 segmentation inside one site (4094 IDs). VXLAN = overlay: L2 segments tunnelled over an L3 fabric, which is why it")
print("pairs with leaf-spine and multi-tenant clouds. check: OK")
