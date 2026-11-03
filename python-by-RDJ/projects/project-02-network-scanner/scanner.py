# Tags: #Python #Project #Cybersecurity #PortScanning #NetworkScanner | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""A multi-threaded TCP connect port scanner with banner grabbing.

LEARNING TOOL, hard-limited to systems you control: it refuses any target that
is not loopback or RFC1918 private space, and there is no override flag.
Scanning hosts you do not own or have written permission to test is illegal.
Standard library only.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor

MAX_PORTS = 2048          # largest number of ports allowed in one run
MAX_THREADS = 100         # hard cap on worker threads
MAX_TIMEOUT = 5.0         # seconds; keeps a run bounded
BANNER_BYTES = 128        # banners are truncated to this many bytes
BANNER_TIMEOUT = 0.3      # seconds to wait for a banner after connecting

# The ONLY networks the scanner will touch. Written out explicitly instead of
# using ipaddress's is_private (which also admits other ranges).
ALLOWED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),     # IPv4 loopback
    ipaddress.ip_network("::1/128"),         # IPv6 loopback
    ipaddress.ip_network("10.0.0.0/8"),      # RFC1918
    ipaddress.ip_network("172.16.0.0/12"),   # RFC1918
    ipaddress.ip_network("192.168.0.0/16"),  # RFC1918
]


class ScanError(Exception):
    """Bad input or a refused target. The CLI turns this into exit code 2."""


def parse_ports(spec: str) -> list[int]:
    """Parse '1-1024,8080' into a sorted, de-duplicated list of ports."""
    ports: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            raise ScanError(f"empty item in port list: {spec!r}")
        try:
            if "-" in part:
                lo_s, hi_s = part.split("-", 1)
                lo, hi = int(lo_s), int(hi_s)
            else:
                lo = hi = int(part)
        except ValueError:
            raise ScanError(f"not a port or range: {part!r}") from None
        if lo > hi:
            raise ScanError(f"range is backwards: {part!r}")
        if lo < 1 or hi > 65535:
            raise ScanError(f"ports must be 1-65535: {part!r}")
        if len(ports) + (hi - lo + 1) > MAX_PORTS * 2:  # stop huge ranges early
            raise ScanError(f"too many ports (max {MAX_PORTS} per run)")
        ports.update(range(lo, hi + 1))
    if len(ports) > MAX_PORTS:
        raise ScanError(f"too many ports: {len(ports)} (max {MAX_PORTS} per run)")
    return sorted(ports)


def is_allowed(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """True only for loopback and RFC1918 addresses."""
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped  # ::ffff:8.8.8.8 must be judged as 8.8.8.8
    return any(ip in net for net in ALLOWED_NETWORKS if net.version == ip.version)


def resolve_and_check(target: str) -> str:
    """Return a verified-safe IP string, or raise ScanError.

    This runs BEFORE any socket is created. An IP literal is parsed locally
    (no DNS). A hostname is resolved, EVERY answer must be allowed, and the
    caller then connects to the checked IP, never the name (no DNS rebinding).
    """
    literal = target.split("%", 1)[0]  # drop an IPv6 zone id such as fe80::1%eth0
    try:
        addrs = [ipaddress.ip_address(literal)]
    except ValueError:
        try:
            infos = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)
        except socket.gaierror as exc:
            raise ScanError(f"cannot resolve {target!r}: {exc}") from None
        addrs = [ipaddress.ip_address(info[4][0].split("%", 1)[0]) for info in infos]
        if not addrs:
            raise ScanError(f"{target!r} resolved to nothing")
    for addr in addrs:
        if not is_allowed(addr):
            raise ScanError(
                f"REFUSED: {target!r} -> {addr} is not loopback or private "
                "(127.0.0.0/8, ::1, 10/8, 172.16/12, 192.168/16). "
                "Only scan machines you own. There is no override."
            )
    return str(addrs[0])


def grab_banner(sock: socket.socket) -> str:
    """Passively read whatever the server volunteers (no data is sent)."""
    sock.settimeout(BANNER_TIMEOUT)
    try:
        data = sock.recv(BANNER_BYTES)
    except (socket.timeout, OSError):
        return ""
    text = data[:BANNER_BYTES].decode("utf-8", errors="replace")
    return text.strip()


def scan_port(ip: str, port: int, timeout: float, banner: bool) -> dict | None:
    """Try one TCP connect. Return a result dict if open, else None."""
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    sock = socket.socket(family, socket.SOCK_STREAM)
    try:
        sock.settimeout(timeout)
        if sock.connect_ex((ip, port)) != 0:
            return None
        return {"port": port, "banner": grab_banner(sock) if banner else None}
    except OSError:
        return None
    finally:
        sock.close()


def scan(ip: str, ports: list[int], timeout: float, threads: int,
         banner: bool) -> list[dict]:
    """Scan ports concurrently; return open ports sorted by port number."""
    with ThreadPoolExecutor(max_workers=threads) as pool:
        results = pool.map(lambda p: scan_port(ip, p, timeout, banner), ports)
        return sorted((r for r in results if r), key=lambda r: r["port"])


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="TCP connect scanner for loopback/private addresses only.")
    p.add_argument("--target", default="127.0.0.1",
                   help="IP or hostname; must be loopback or RFC1918 (default 127.0.0.1)")
    p.add_argument("--ports", default="1-1024",
                   help=f"e.g. 1-1024,8080 (max {MAX_PORTS} ports; default 1-1024)")
    p.add_argument("--timeout", type=float, default=0.5,
                   help=f"connect timeout in seconds (0-{MAX_TIMEOUT}; default 0.5)")
    p.add_argument("--threads", type=int, default=50,
                   help=f"worker threads (1-{MAX_THREADS}; default 50)")
    p.add_argument("--no-banner", action="store_true", help="skip banner grabbing")
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if not 0 < args.timeout <= MAX_TIMEOUT:
            raise ScanError(f"--timeout must be in (0, {MAX_TIMEOUT}]")
        if not 1 <= args.threads <= MAX_THREADS:
            raise ScanError(f"--threads must be 1-{MAX_THREADS}")
        ports = parse_ports(args.ports)
        ip = resolve_and_check(args.target)  # safety gate: before any connect
    except ScanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    start = time.perf_counter()
    found = scan(ip, ports, args.timeout, args.threads, not args.no_banner)
    elapsed = round(time.perf_counter() - start, 3)

    if args.json:
        print(json.dumps({
            "target": args.target, "resolved": ip, "ports_scanned": len(ports),
            "open": found, "elapsed_seconds": elapsed}, indent=2))
    else:
        print(f"Scanning {args.target} ({ip}): {len(ports)} ports, "
              f"{args.threads} threads, timeout {args.timeout}s")
        for r in found:
            extra = f"  banner: {r['banner']!r}" if r["banner"] else ""
            print(f"  {r['port']}/tcp open{extra}")
        print(f"{len(found)} open, {len(ports) - len(found)} closed/filtered "
              f"(elapsed {elapsed}s, a measurement)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
