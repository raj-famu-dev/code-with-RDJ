# Tags: #Python #Project #Cybersecurity #PortScanning #Tests #scanner | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Tests for scanner.py. Only 127.0.0.1 servers started here are ever contacted."""

import json
import socket
import threading

import pytest

import scanner


class Server:
    """Tiny loopback server on port 0. Sends `banner` on connect, if given."""

    def __init__(self, banner: bytes | None):
        self.banner = banner
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(16)
        self.sock.settimeout(0.2)
        self.port = self.sock.getsockname()[1]
        self.stop = threading.Event()
        self.conns: list[socket.socket] = []
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        while not self.stop.is_set():
            try:
                conn, _ = self.sock.accept()
            except (socket.timeout, OSError):
                continue
            if self.banner:
                conn.sendall(self.banner)
            self.conns.append(conn)  # keep open and silent until close()

    def close(self):
        self.stop.set()
        self.thread.join()
        for c in self.conns:
            c.close()
        self.sock.close()


@pytest.fixture
def servers():
    banner, silent = Server(b"SSH-2.0-TestServer\r\n"), Server(None)
    yield banner, silent
    banner.close()
    silent.close()


@pytest.fixture
def closed_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()  # nothing listens here now
    return port


def test_open_closed_and_banner(servers, closed_port):
    banner, silent = servers
    ports = sorted([banner.port, silent.port, closed_port])
    found = scanner.scan("127.0.0.1", ports, 0.5, 8, True)
    by_port = {r["port"]: r["banner"] for r in found}
    assert set(by_port) == {banner.port, silent.port}
    assert closed_port not in by_port
    assert by_port[banner.port] == "SSH-2.0-TestServer"
    assert by_port[silent.port] == ""


def test_no_banner_flag(servers):
    banner, _ = servers
    (r,) = scanner.scan("127.0.0.1", [banner.port], 0.5, 1, False)
    assert r["banner"] is None


def test_banner_truncated_and_decode_errors_replaced():
    srv = Server(b"\xff" + b"A" * 500)
    try:
        (r,) = scanner.scan("127.0.0.1", [srv.port], 0.5, 1, True)
    finally:
        srv.close()
    assert "�" in r["banner"]
    assert len(r["banner"].encode("utf-8")) <= 128 + 2  # replacement char is 3 bytes


def test_parse_ports():
    assert scanner.parse_ports("80") == [80]
    assert scanner.parse_ports("1-3,8080,2") == [1, 2, 3, 8080]
    assert len(scanner.parse_ports("1-1024")) == 1024


@pytest.mark.parametrize("bad", ["0", "65536", "5-1", "a", "1-", "", "1,,2",
                                 "1-65535", "1-2049"])
def test_parse_ports_rejects(bad):
    with pytest.raises(scanner.ScanError):
        scanner.parse_ports(bad)


@pytest.mark.parametrize("ip", ["127.0.0.1", "127.9.9.9", "::1", "10.1.2.3",
                                "172.16.0.5", "172.31.255.255", "192.168.1.1"])
def test_allowed(ip):
    assert scanner.resolve_and_check(ip) == ip


@pytest.mark.parametrize("ip", ["8.8.8.8", "1.1.1.1", "172.32.0.1", "192.169.0.1",
                                "169.254.1.1", "0.0.0.0", "2001:4860:4860::8888",
                                "::ffff:8.8.8.8"])
def test_refused_ips(ip):
    with pytest.raises(scanner.ScanError, match="REFUSED"):
        scanner.resolve_and_check(ip)


def test_public_ip_refused_before_any_packet(monkeypatch, capsys):
    """If the safety gate ever let a socket be created, this test fails."""
    def boom(*a, **k):
        raise AssertionError("network access attempted for a refused target")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    assert scanner.main(["--target", "8.8.8.8", "--ports", "53,80"]) == 2
    assert "REFUSED" in capsys.readouterr().err


def test_hostname_resolving_to_public_is_refused(monkeypatch):
    """Fake resolver answers with a public IP; no socket may be created."""
    monkeypatch.setattr(socket, "getaddrinfo",
                        lambda *a, **k: [(2, 1, 6, "", ("8.8.8.8", 0))])
    monkeypatch.setattr(socket, "socket", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("socket created")))
    assert scanner.main(["--target", "example.test"]) == 2


def test_mixed_resolution_refused(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [
        (2, 1, 6, "", ("127.0.0.1", 0)), (2, 1, 6, "", ("8.8.8.8", 0))])
    with pytest.raises(scanner.ScanError):
        scanner.resolve_and_check("sneaky.test")


def test_caps_enforced(capsys):
    assert scanner.main(["--threads", "101"]) == 2
    assert scanner.main(["--threads", "0"]) == 2
    assert scanner.main(["--ports", "1-5000"]) == 2
    assert scanner.main(["--timeout", "60"]) == 2


def test_no_force_flag():
    with pytest.raises(SystemExit) as exc:
        scanner.main(["--target", "8.8.8.8", "--force"])
    assert exc.value.code == 2


def test_json_shape(servers, capsys):
    banner, silent = servers
    ports = f"{banner.port},{silent.port}"
    assert scanner.main(["--ports", ports, "--json", "--timeout", "0.5"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert set(data) == {"target", "resolved", "ports_scanned", "open",
                         "elapsed_seconds"}
    assert data["target"] == data["resolved"] == "127.0.0.1"
    assert data["ports_scanned"] == 2
    assert [r["port"] for r in data["open"]] == sorted([banner.port, silent.port])
    assert all(set(r) == {"port", "banner"} for r in data["open"])


def test_text_output(servers, capsys):
    banner, _ = servers
    assert scanner.main(["--ports", str(banner.port)]) == 0
    out = capsys.readouterr().out
    assert f"{banner.port}/tcp open" in out and "SSH-2.0-TestServer" in out
