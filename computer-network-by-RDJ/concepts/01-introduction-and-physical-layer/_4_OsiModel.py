# Tags: #Python #ComputerNetworks #PhysicalLayer #OsiModel | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""The OSI reference model: 7 layers, their jobs, PDU names, example protocols and
devices, plus a layer-stack simulator that wraps (encapsulates) and unwraps
(decapsulates) a message. Implements the 'OSI model' syllabus topic."""
from dataclasses import dataclass


# ===== SECTION 1: THE SEVEN LAYERS =====
print("===== SECTION 1: THE SEVEN LAYERS =====")


@dataclass(frozen=True)
class Layer:
    number: int
    name: str
    pdu: str
    job: str
    protocols: str
    device: str


LAYERS = [
    Layer(7, "Application", "data", "services for the user's program", "HTTP, SMTP, DNS, FTP", "gateway"),
    Layer(6, "Presentation", "data", "format, encryption, compression", "TLS (placed here by some books), JPEG, ASCII", "gateway"),
    Layer(5, "Session", "data", "open, manage, close dialogs; sync points", "NetBIOS, RPC, PPTP (examples)", "gateway"),
    Layer(4, "Transport", "segment / user datagram", "end-to-end delivery, ports, reliability", "TCP, UDP", "gateway / firewall"),
    Layer(3, "Network", "packet", "logical addressing, routing", "IP, ICMP, OSPF", "router"),
    Layer(2, "Data Link", "frame", "hop-to-hop delivery, MAC addressing, error detection", "Ethernet, PPP, ARP*", "switch, bridge, NIC"),
    Layer(1, "Physical", "bit", "move raw bits as signals", "RJ45, fibre, 802.3 signalling", "hub, repeater, cable"),
]
print(f"{'#':<3}{'layer':<13}{'PDU':<24}{'job'}")
for ly in LAYERS:
    print(f"{ly.number:<3}{ly.name:<13}{ly.pdu:<24}{ly.job}")
print()
print(f"{'layer':<13}{'example protocols':<48}{'device'}")
for ly in LAYERS:
    print(f"{ly.name:<13}{ly.protocols:<48}{ly.device}")
print("Transport PDU: 'segment' for TCP, 'datagram' (user datagram) for UDP.")
print("* ARP is often described as sitting between layers 2 and 3.")
words = "Please Do Not Throw Sausage Pizza Away".split()
print("Mnemonic, layer 1 up to 7:", " ".join(f"{i + 1}={w}" for i, w in enumerate(words)))
print("Top down (7 to 1): All People Seem To Need Data Processing")
mn = "".join(w[0] for w in words)
initials = "".join(ly.name[0] for ly in reversed(LAYERS))
assert mn == initials, (mn, initials)
print(f"check: mnemonic initials {mn} == layer initials {initials}: OK")


# ===== SECTION 2: ENCAPSULATION (WRAP) =====
print("\n===== SECTION 2: ENCAPSULATION (WRAP) =====")

# Which layers add a header, and which also add a trailer.
HEADER_TAG = {7: "AH", 6: "PH", 5: "SH", 4: "TH", 3: "NH", 2: "DH", }
TRAILER = {2: "DT"}


def wrap(message: str, verbose: bool = True) -> str:
    """Send side: go DOWN from layer 7 to 1, each layer adds its header (L2 adds a trailer too)."""
    pdu = message
    for n in range(7, 0, -1):
        if n in HEADER_TAG:
            pdu = f"[{HEADER_TAG[n]}]{pdu}"
        if n in TRAILER:
            pdu = f"{pdu}[{TRAILER[n]}]"
        if verbose:
            name = next(ly.name for ly in LAYERS if ly.number == n)
            note = "(bits on the wire)" if n == 1 else ""
            print(f"  L{n} {name:<12} -> {pdu} {note}".rstrip())
    return pdu


def unwrap(frame: str, verbose: bool = True) -> str:
    """Receive side: go UP from layer 1 to 7, each layer strips its own header/trailer."""
    pdu = frame
    for n in range(1, 8):
        if n in TRAILER:
            tag = f"[{TRAILER[n]}]"
            if not pdu.endswith(tag):
                raise ValueError(f"layer {n}: expected trailer {tag} in {pdu!r}")
            pdu = pdu[: -len(tag)]
        if n in HEADER_TAG:
            tag = f"[{HEADER_TAG[n]}]"
            if not pdu.startswith(tag):
                raise ValueError(f"layer {n}: expected header {tag} at the front of {pdu!r}")
            pdu = pdu[len(tag):]
        if verbose:
            name = next(ly.name for ly in LAYERS if ly.number == n)
            print(f"  L{n} {name:<12} <- {pdu}")
    return pdu


msg = "HELLO"
print("Sender wraps:")
on_wire = wrap(msg)


# ===== SECTION 3: DECAPSULATION (UNWRAP) AND PEER-TO-PEER VIEW =====
print("\n===== SECTION 3: DECAPSULATION (UNWRAP) AND PEER-TO-PEER VIEW =====")
print("Receiver unwraps:")
got = unwrap(on_wire)
assert got == msg
print(f"delivered {got!r}; check: OK")
print("Peer-to-peer rule: each layer only reads the header written by the SAME layer on the other host.")
print("Layer 3 of the sender 'talks to' layer 3 of the receiver, but the data physically goes down and up the stacks.")

# Trap: unwrapping in the wrong order (or with a wrong layer) fails.
print("\nTrap: the frame arrives with its data-link header damaged/missing, so layer 2 cannot do its job:")
try:
    wrong = on_wire[len("[DH]"):]   # layer-2 header lost in transit
    unwrap(wrong, verbose=False)
except ValueError as exc:
    print("  ValueError ->", exc)


# ===== SECTION 4: INTERMEDIATE DEVICES AND LAYERS =====
print("\n===== SECTION 4: INTERMEDIATE DEVICES AND LAYERS =====")
print("Which layers does each device unwrap? (it opens the frame only as high as its job needs)")
DEVICE_TOP = {"hub/repeater": 1, "switch/bridge": 2, "router": 3, "gateway/proxy": 7}
names = {ly.number: ly.name for ly in LAYERS}
for dev, top in DEVICE_TOP.items():
    seen = ", ".join(f"L{n}" for n in range(1, top + 1))
    print(f"  {dev:<14} reads up to L{top} ({names[top]:<11}) -> processes {seen}")
print("Router example: frame arrives, L2 stripped, L3 chooses next hop, a NEW L2 header is attached on the way out.")
frame_in = "[DH-A]" + "[NH]" + "[TH]" + "data" + "[DT-A]"
frame_out = frame_in.replace("DH-A", "DH-B").replace("DT-A", "DT-B")
print("  in :", frame_in)
print("  out:", frame_out, "(only the data-link parts changed; L3 and above untouched, except TTL in real IP)")


# ===== SECTION 5: WORKED EXAMPLE =====
print("\n===== SECTION 5: WORKED EXAMPLE =====")
payload = "GET /index"
headers = {7: 4, 6: 2, 5: 2, 4: 20, 3: 20, 2: 14}   # illustrative header sizes in bytes
trailer = 4
total = len(payload) + sum(headers.values()) + trailer
print(f"payload {len(payload)} B + headers {sum(headers.values())} B + L2 trailer {trailer} B = {total} B on the wire")
print(f"overhead = {total - len(payload)} B = {(total - len(payload)) / total:.0%} of the frame")
assert total == 76
print("check: OK (header sizes are illustrative; see _5_TcpIpModelAndEncapsulation for real ones)")
