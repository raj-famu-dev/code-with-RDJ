# `_7_NetworkToolsAndTroubleshooting.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

> Scope: the only sockets opened are connections to 127.0.0.1 servers that the script starts itself; the one name lookup is `localhost`. A guard function refuses any other host. Run real tools such as nmap only against systems you own or have written permission to test.

## Concept
Network troubleshooting is the discipline of finding which layer or component is failing, using tools that each answer one specific question. Knowing what each tool measures, and which layer it exercises, lets you narrow a vague complaint ("the internet is down") down to one cause quickly.

**The tools.**

| Tool | Layer | Answers |
|---|---|---|
| `ip addr`, `ip link`, `ip route` (older: `ifconfig`, `route`) | 1-3 | Is the link up? What IP, mask, MAC, default gateway do I have? |
| `arp -a`, `ip neigh` | 2-3 | Which MAC is cached for an IP on my LAN? |
| `ping` | 3 | Does the host answer ICMP echo? Round-trip time, packet loss. |
| `traceroute` (`tracert` on Windows) | 3 | Which routers lie on the path? It sends probes with increasing TTL and records the ICMP Time Exceeded replies. |
| `nslookup`, `dig` | 7 (DNS) | Does a name resolve, to which records, via which server? |
| `netstat`, `ss` | 4 | Listening ports and open connections on this machine, with the owning process (`ss -tulpn`). |
| `curl` | 7 | Does the application respond? HTTP status, headers, TLS and timing (`-v`, `-w`). |
| `nmap` | 3-4 (+7) | Which ports and services are open on a host. Only on systems you own or are authorised to test; scanning others can be illegal. |
| Wireshark / tcpdump | 2-7 | What is actually on the wire: capture and decode. |

**Method (bottom-up).** (1) Define the symptom precisely and decide the scope (one user, one site, everyone). (2) Start at the physical/link layer: cable, Wi-Fi association, link light. (3) Network layer: do I have an IP, can I reach the default gateway, can I reach a remote IP? (4) Name resolution: does the name resolve (if the IP works but the name does not, it is DNS). (5) Transport: is the port open? (6) Application: does the service return correct data? Change one thing at a time, document what you did, and keep a rollback. Top-down and divide-and-conquer (start in the middle, such as pinging the gateway) are alternatives; the point is to be systematic.

**What each answer means.** A closed port answers with a TCP RST (connection refused); a firewall that silently drops answers nothing (timeout, "filtered"). `traceroute` rows of `*` mean no reply within the timeout: a filter may be dropping probes or replies even though traffic passes. `ping` working does not prove the application works (ICMP may be allowed while TCP is blocked) and `ping` failing does not prove it is down (ICMP may be filtered). Latency summaries use min and median because a mean is distorted by outliers. Loopback latency is a property of the local machine only and tells you nothing about a real path.

Typical exam questions: which tool for which layer; how does traceroute work; steps of a troubleshooting method; difference between ping failing and a port being closed; what does `ss -tulpn` show.

## Full Line-by-Line Breakdown

### SECTION 1: THE TOOLBOX AND THE LAYERS
Prints the table above with an example command per tool. Nothing is executed.

```text
===== SECTION 1: THE TOOLBOX AND THE LAYERS =====
Tool                 Layer     Question it answers
ip / ifconfig        1-3       Is the interface up? What IP, mask, MAC, routes do I have?
                               e.g. ip addr, ip route (ifconfig is the older tool)
arp / ip neigh       2-3       Which MAC does this IP on my LAN map to?
                               e.g. ip neigh
ping                 3         Is the host reachable by ICMP echo, and what is the RTT / loss?
                               e.g. ping -c 4 <host>
traceroute           3         Which routers lie on the path, where does it stop?
                               e.g. traceroute <host> (tracert on Windows)
nslookup / dig       7 (DNS)   Does the name resolve, to what, via which server?
                               e.g. dig <name>; nslookup <name>
netstat / ss         4         Which ports are listening / which connections exist on THIS machine?
                               e.g. ss -tulpn
curl                 7         Does the application answer? Status code, headers, TLS, timing.
                               e.g. curl -v <url>
nmap                 3-4 (+7)  Which ports/services are open on a host YOU are authorised to test?
                               e.g. only on systems you own or have written permission for
Wireshark / tcpdump  2-7       What exactly is on the wire (packet capture + decode)?
                               e.g. needs capture privileges, own networks only
This file does not run any of these. It implements the IDEAS (port check, latency, TTL walk) on loopback only.
```

### SECTION 2: OWN PORT-CHECK ON LOOPBACK (A MEASUREMENT)
`require_loopback` raises `ValueError` for any host except 127.0.0.1. `EchoServer` binds 127.0.0.1 on port 0 (the OS picks a free port), listens in a background thread with a 0.2 s accept timeout and a stop event, echoes bytes back, and is always stopped and joined by its context manager. `port_check` calls `connect_ex` with a timeout and maps the result: 0 is open, connection refused (errno 111 on Linux, 61 on macOS, 10061 on Windows) is closed, and anything else (a timeout) is "filtered/timeout". To get a closed port, the script binds a socket to port 0, reads the port number, and closes it. The guard demo calls the function with a documentation address (192.0.2.1); it raises before any socket exists.

```text
===== SECTION 2: OWN PORT-CHECK ON LOOPBACK (A MEASUREMENT) =====
port_check(127.0.0.1, <our echo server>) -> open
port_check(127.0.0.1, <a port nobody listens on>) -> closed
check: OK (a listening port accepts; a closed one answers RST = 'connection refused')
guard works: refusing to contact '192.0.2.1': this module measures 127.0.0.1 only
A SYN that gets NO answer at all (firewall DROP) shows up as a timeout, which is why 'filtered' differs from 'closed'.
```

### SECTION 3: OWN LATENCY MEASURE (A MEASUREMENT)
Twenty TCP connects and 20 echo round trips on one connection are timed with `time.perf_counter`. The correctness checks (20 results, all echoes identical, all times positive) are deterministic; the printed numbers are labelled measurements and change on every run. The min, median and max are reported rather than the mean. These describe only this machine's loopback: no wire, no router, no propagation delay.

```text
===== SECTION 3: OWN LATENCY MEASURE (A MEASUREMENT) =====
20 TCP connects and 20 echo round trips completed, every echo returned the exact bytes. check: OK
[measurement, varies per run] TCP connect: min=0.015 ms median=0.055 ms max=1.833 ms
[measurement, varies per run] echo RTT:    min=0.033 ms median=0.034 ms max=0.210 ms
These numbers describe this machine's loopback only. They say nothing about real network latency, which is
dominated by propagation + queuing (module 01). Use min/median, not mean, because one slow outlier skews it.
server stopped, thread joined, sockets closed
```

### SECTION 4: NAME RESOLUTION ON 'localhost' ONLY
`resolve_local` refuses any name but `localhost` and calls `socket.getaddrinfo`. `localhost` is normally answered from the hosts file, so no DNS packet leaves the machine. The set of addresses can include 127.0.0.1 and/or ::1 depending on the system, which is why the output may differ between computers. The text explains what `dig` and `nslookup` add and the "ping IP works, ping name fails" diagnosis.

```text
===== SECTION 4: NAME RESOLUTION ON 'localhost' ONLY =====
getaddrinfo('localhost') addresses (set depends on the machine's hosts file): ['127.0.0.1']
check: OK (localhost maps to the loopback address 127.0.0.1 and/or ::1)
'localhost' is answered from the local hosts file / resolver config, no DNS query leaves the machine.
What dig/nslookup add: ask a chosen DNS server, see record types (A, AAAA, MX, NS, CNAME), TTLs and the answer path.
Diagnostic trick: if ping <IP> works but ping <name> fails, the fault is DNS, not connectivity.
```

### SECTION 5: TTL WALK (TRACEROUTE LOGIC) AND PING STATISTICS
`probe(ttl)` models a made-up four-router path: the router where the TTL reaches zero drops the packet and reports ICMP Time Exceeded; a TTL large enough reaches the destination and gets an echo reply. Running TTL 1, 2, 3, 4 reveals the path hop by hop; with a filter at hop 3, hops 3 and later show `*`. The ping summary uses fixed example data (6 probes, one lost): loss = 1/6 = 16.7 percent, and min/avg/max are computed from the 5 received values.

```text
===== SECTION 5: TTL WALK (TRACEROUTE LOGIC) AND PING STATISTICS =====
Made-up path; traceroute sends probes with TTL 1, 2, 3, ... and records who answers:
  TTL=1: 192.168.1.1 (home router) ICMP Time Exceeded
  TTL=2: 10.20.0.1 (ISP edge) ICMP Time Exceeded
  TTL=3: 172.31.5.2 (backbone) ICMP Time Exceeded
  TTL=4: 203.0.113.9 (destination) reached, ICMP Echo Reply
Same path with the third router silently dropping everything (a filter):
  TTL=1: 192.168.1.1 (home router) ICMP Time Exceeded
  TTL=2: 10.20.0.1 (ISP edge) ICMP Time Exceeded
  TTL=3: * (no reply)
  TTL=4: * (no reply)
check: OK (a row of '*' shows where the path is filtered, not necessarily where it is broken)
Sample ping run (fixed example data): sent=6 received=5 loss=16.7% min/avg/max = 20.7/24.1/35.2 ms
check: OK (1 lost of 6 = 16.7% loss)
```

### SECTION 6: BOTTOM-UP TROUBLESHOOTING DECISION TABLE
`diagnose` walks the ordered list of checks (link, IP, gateway, remote IP, DNS, port, application) and returns the first failing layer with the next action. Six scenarios show the results, including the DNS case (IP pings work, names do not) and the crashed server (host reachable, port closed). The two traps at the end describe the ICMP misleading cases.

```text
===== SECTION 6: BOTTOM-UP TROUBLESHOOTING DECISION TABLE =====
Method: define the symptom, work UP from the physical layer, change one thing at a time, document.
  cable unplugged                    -> L1/L2: no link
                                        next: check cable/Wi-Fi association, switch port, NIC (ip link)
  DHCP failed (169.254.x.x)          -> L3: no valid IP configuration
                                        next: check DHCP, mask, gateway (ip addr, dhclient logs)
  can ping an IP but not a name      -> L7 DNS: IP works but the name does not resolve
                                        next: check resolver config; dig @server name
  web server process crashed         -> L4: host reachable but the port is closed or filtered
                                        next: check the service is listening (ss -tulpn) and firewall rules
  HTTP 500 from the app              -> L7: port open but the application fails
                                        next: read the app logs; curl -v for status and headers
  everything passes                  -> no fault found at these layers
                                        next: problem may be intermittent: monitor and capture
check: OK
TRAP 1: 'ping works but the website does not' = ICMP is allowed but TCP 80/443 is not (or the app is down).
TRAP 2: 'ping fails but the website works' = ICMP is blocked by a firewall; ping is not proof of reachability either way.
Loopback analogue of 'host is up but the port is not': our server port was open while a dead port was closed - same host, different answers.
```

## Worked Example
**Q.** A ping run sent 6 probes and received replies of 21.4, 20.9, 22.1, 20.7 and 35.2 ms; one probe got no reply. Give the loss percentage, min/avg/max and the median of received RTTs, and say what the 35.2 suggests.

1. Loss = 1 / 6 = 16.7 percent.
2. min = 20.7 ms, max = 35.2 ms, average = (21.4 + 20.9 + 22.1 + 20.7 + 35.2) / 5 = 120.3 / 5 = 24.06, which prints as 24.1 ms.
3. Sorted received values: 20.7, 20.9, 21.4, 22.1, 35.2; the median is 21.4 ms.
4. The 35.2 ms value is an outlier that pulls the average above every other sample; use the median, then look for queuing or a busy link.

The code printed loss 16.7 percent and min/avg/max = 20.7/24.1/35.2.

## Key Rules / Gotchas Recap
- Work bottom-up, change one thing at a time, document.
- ping tests ICMP only; "ping works" is not "service works", and "ping fails" is not "host down".
- Closed port = RST (fast refusal); filtered = silence (timeout).
- `*` in traceroute means no reply, not necessarily a failure.
- DNS fault signature: connection by IP works, by name fails.
- Use min and median for latency; label measurements as measurements.
- Use scanners and sniffers only on your own systems or with written permission.

## Why This Matters
These tools are the first things used in any outage, from a laptop to an inference cluster, and the habit of narrowing by layer turns guesswork into a short checklist. Writing a small port check and latency probe yourself, as here, is how monitoring and health-check code (readiness probes for model servers) works.
