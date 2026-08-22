
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

def find_node_section_v4(p, limit=None):
    """Scan [1]...{0..8 u32}...[136]...count combos; validate 52/92/132B record streams."""
    lim = limit or (len(p) - 100)
    cands = []
    i = 0
    while i < lim - 40:
        if u32(p, i) == 1:
            for gap in range(1, 9):
                j = i + gap * 4
                if j + 24 <= len(p) and u32(p, j) == 136:
                    n = u32(p, j + 4)
                    if 1 <= n <= 10_000_000:
                        cands.append((i, j, n))
        i += 4
    best = None
    for hi, hj, count in cands[:40]:
        first = None
        for base in range(hi - 32, hj + 16, 4):
            if base < 0: continue
            for stride in (52, 92, 132):
                ok = 0; bad = 0
                for k in range(min(count, 60)):
                    rec = base + k * stride
                    if rec + stride > len(p):
                        break
                    nid = u32(p, rec + 8)
                    x = d64(p, rec + 20)
                    if 1 <= nid <= 10_000_000 and abs(x) < 1e9:
                        ok += 1
                    else:
                        bad += 1
                        if bad > 4:
                            break
                if ok >= 45 and bad <= 1:
                    return (hi, count, base, stride)
    return None

for fname in ["molding1.hm", "truck.hm", "car_section.hm", "cover.hm", "SEAT_MODEL.hm"]:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    p = load_payload(path)
    res = find_node_section_v4(p)
    print(f"== {fname}: {res}")
