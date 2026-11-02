# `_6_PortCheckingOnLocalhost.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A TCP port is "open" when a program is listening on it and a connection attempt succeeds, and "closed" when the machine actively refuses the attempt. `socket.connect_ex()` tries to connect and returns an error code instead of raising an exception, which makes it a simple building block for port checks. In this file the checker only ever probes **your own machine (127.0.0.1)**: it refuses any other address on purpose. Scanning systems you do not own or have written permission to test can be illegal and violates most network policies.

## Full Line-by-Line Breakdown

### SECTION 1: the rule that shapes this whole file
The file states the rule up front: probe only systems you own or are explicitly authorised to test. Unauthorized scanning can violate computer-misuse laws (for example the US Computer Fraud and Abuse Act) and provider terms of service. This is not legal advice; the safe practice is to use localhost, your own virtual machines, or legal practice platforms and CTFs. For a real engagement, authorization means written scope and permission.

```text
=== SECTION 1: the rule that shapes this whole file ===
Only YOUR machine is checked here. Probing someone else's host without
permission can be illegal (e.g. under the US CFAA) and violates most ISP rules.
Learn on 127.0.0.1, your own VMs, or legal labs/CTF platforms.

```

### SECTION 2: a checker that refuses non-loopback hosts
`check_port` first calls `ipaddress.ip_address(host).is_loopback`. If the address is not loopback it raises `ValueError` **before creating any socket**. The demonstration passes `192.0.2.1`, an address from the TEST-NET-1 range reserved for documentation, and shows it being refused; nothing is sent anywhere. Building safety into the function means a future mistake cannot turn it into a scanner. When it is allowed, the function opens a TCP socket with a timeout and interprets the return code of `connect_ex`: `0` means open, `errno.ECONNREFUSED` means closed.

```text
=== SECTION 2: a checker that refuses non-loopback hosts ===
guard works -> refusing to probe non-loopback host '192.0.2.1'
(the guard raised BEFORE any socket was created; nothing was sent anywhere)

```

### SECTION 3: an open port we start ourselves
The script starts its own listener on port `0`, learns the port number, and runs a thread that accepts and immediately closes connections. `check_port` on that port returns `open`. A return value of `0` from `connect_ex` means the TCP three-way handshake completed.

```text
=== SECTION 3: an open port we start ourselves ===
connect_ex on our listener: open
0 from connect_ex means success; the three-way handshake completed.

```

### SECTION 4: a port we KNOW is closed
To get a port that is certainly closed, the script binds a socket to port `0`, notes the port, then closes it. Nothing is listening there any more, so `connect_ex` returns `ECONNREFUSED`. The exact number differs by operating system (111 on Linux, 61 on macOS, 10061 on Windows), so the code compares against `errno.ECONNREFUSED`, never a hard-coded number. (A different program could grab that port in the meantime; on a quiet machine this is extremely unlikely, but it is why the script says "know" with a short window.)

```text
=== SECTION 4: a port we KNOW is closed ===
connect_ex on a freed port: closed
raw return code == errno.ECONNREFUSED: True
errno value itself is OS-specific (Linux 111, macOS 61, Windows 10061);
compare against errno.ECONNREFUSED, never a hard-coded number.

```

### SECTION 5: connect vs connect_ex
`connect()` raises `ConnectionRefusedError` on failure, `connect_ex()` returns the error code. The second form is convenient when you are testing many outcomes and do not want exception handling for each.

```text
=== SECTION 5: connect vs connect_ex ===
connect()    -> raises ConnectionRefusedError
connect_ex() -> returns an error code, no exception (handy for loops)

```

### SECTION 6: checking a small list of ports
Two ports are checked: our own listener (`open`) and the freed port (`closed`). The script deliberately does not loop through ranges of ports or accept a host from user input.

```text
=== SECTION 6: checking a small list of ports ===
  known-closed port : closed
  our listener      : open
Only two ports, both ours. We do NOT sweep ranges, and we never take a
host from user input.

```

### SECTION 7: timeouts and what 'filtered' means
A **closed** port answers immediately with a reset. A **filtered** port is behind a firewall that silently drops packets, so there is no answer and the attempt ends only by timeout. Loopback is not firewalled this way, so this is explained rather than demonstrated. Always set a timeout so a check cannot hang.

```text
=== SECTION 7: timeouts and what 'filtered' means ===
closed = host actively answers 'nobody here' (RST) -> ECONNREFUSED, fast.
filtered = a firewall silently drops packets -> no answer -> timeout, slow.
On loopback you will essentially never see 'filtered', so we only explain it.
A short timeout keeps a checker from hanging; it must never be left unset.

```

### SECTION 8: cleanup
One more connection lets the acceptor thread finish; the thread is joined and the listener closed.

```text
=== SECTION 8: cleanup ===
thread joined: True | connections the listener accepted: 2
listener closed; fileno = -1
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| Test a port | `try (Socket s = new Socket()) { s.connect(new InetSocketAddress(host, port), timeoutMs); }` and catch `ConnectException` / `SocketTimeoutException` | `s.connect_ex((host, port))` returns `0` or an errno; no exception |
| Closed vs filtered | `ConnectException: Connection refused` vs `SocketTimeoutException` | `ECONNREFUSED` code vs timeout (a timeout error or a non-zero code, depending on platform) |
| Timeout | Passed to `connect(addr, timeout)` | `settimeout()` before connecting |
| Loopback check | `InetAddress.getByName(h).isLoopbackAddress()` | `ipaddress.ip_address(h).is_loopback` |
| Error numbers | Not exposed; you get exception types | Exposed via `errno` module (OS-specific values) |
| Checked exceptions | `IOException` family must be handled | Not enforced |

## Key Rules / Gotchas Recap

- Only check hosts you own or are explicitly authorised to test; here, only `127.0.0.1`.
- Put the loopback guard inside the function so it cannot be bypassed by accident.
- Compare against `errno.ECONNREFUSED`, never a literal number.
- `connect_ex` returns `0` on success, an errno on failure.
- Closed means refused quickly; filtered means silence and a timeout.
- Always set a timeout and close the socket.
- No range sweeps, no user-supplied hosts in this learning code.

## Why This Structure Exists
Understanding open, closed and filtered ports is core to both operating services and defensive security, and doing it on your own machine builds the skill without risk. The legal/ethical rule is part of the technique: professional security work starts with scope and permission, and this file makes that habit part of the code itself.
