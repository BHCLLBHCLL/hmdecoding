import gzip, struct, os
from pathlib import Path

D = Path("corpus/synthetic")
files = sorted(D.glob("*.hm"))
payloads = {}
for f in files:
    raw = f.read_bytes()
    p = gzip.decompress(raw[12:])
    payloads[f.stem] = p
    ver = struct.unpack_from("<d", p, 4)[0]
    print(f"{f.stem:24s} comp={len(raw):6d} payload={len(p):6d} dbver={ver:.2f}")

def changed_regions(a, b, width=8):
    """Return list of (start, end) byte ranges where a and b differ, aligned to width."""
    n = min(len(a), len(b))
    regions = []
    start = None
    for i in range(0, n, width):
        if a[i:i+width] != b[i:i+width]:
            if start is None:
                start = i
        else:
            if start is not None:
                regions.append((start, i + width))
                start = None
    if start is not None:
        regions.append((start, len(a) if len(a) > len(b) else len(b)))
    # tail difference beyond min length
    if len(a) != len(b):
        regions.append((n, max(len(a), len(b))))
    return regions

def show(a, b, name):
    regs = changed_regions(a, b)
    print(f"--- {name}: {len(regs)} changed regions")
    for s, e in regs[:12]:
        print(f"    0x{s:04x}..0x{e:04x} ({e-s} bytes)")
        # show bytes of b in that region
        print(f"      B: {b[s:min(e, s+32)].hex()}")
        if e - s <= 64:
            print(f"      A: {a[s:min(e, s+32)].hex()}")

# chain diffs
names = ["v1913_00_empty", "v1913_01_n1", "v1913_02_n4a", "v1913_02_n4b", "v1913_03_t1", "v1913_04_t2", "v1913_05_c2", "v1913_06_c3"]
for i in range(len(names) - 1):
    show(payloads[names[i]], payloads[names[i+1]], f"{names[i]} -> {names[i+1]}")
