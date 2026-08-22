
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

def find_node_section_v3(p, head_only=True):
    cands = []
    for i in range(0, len(p) - 40):
        if u32(p, i + 8) == 1 and u32(p, i + 12) == 136:
            n = u32(p, i + 16)
            if 1 <= n <= 10_000_000:
                cands.append((i, n))
    best = None
    for hdr, count in cands[:16]:
        for base in range(hdr + 20, hdr + 72, 4):
            for stride in range(52, 264, 4):
                ok = 0; bad = 0
                for k in range(min(count, 80)):
                    rec = base + k * stride
                    if rec + stride > len(p):
                        break
                    nid = u32(p, rec + 8)
                    x = d64(p, rec + 20)
                    if 1 <= nid <= 10_000_000 and abs(x) < 1e9:
                        ok += 1
                    else:
                        bad += 1
                        if bad > 5:
                            break
                if ok >= 50 and bad <= 2:
                    return (hdr, count, base, stride)
    return None

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
print("molding1:", find_node_section_v3(p))

# structural scan on truck front region
p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
print("\ntruck structural scan 0..11M...")
best = None
limit = 11084188
# candidate: [0][id][0][0] then coords; scan 4-byte aligned starts only, stride 52/92/132/172/212/252
for stride in (52, 92, 132, 172, 212, 252):
    for base in range(0, min(limit, len(p2) - 100 * stride), 4):
        ok = 0
        for k in range(20):
            rec = base + k * stride
            a = u32(p2, rec)
            nid = u32(p2, rec + 8)
            if a == 0 and 1 <= nid <= 10_000_000 and abs(d64(p2, rec + 20)) < 1e9:
                ok += 1
            else:
                break
        if ok >= 15:
            print(f"  stride={stride} base={base} ok={ok}")
            best = (stride, base, ok)
            break
    if best:
        break
if not best:
    print("  no structural hit with stride in", (52, 92, 132, 172, 212, 252))
