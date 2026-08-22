
import sys, json, os, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

def find_node_section_v2(p):
    """[1][136][count] header; records 52 + 40*k bytes."""
    cands = []
    for i in range(0, len(p) - 40):
        if u32(p, i + 8) == 1 and u32(p, i + 12) == 136:
            n = u32(p, i + 16)
            if 1 <= n <= 10_000_000:
                cands.append((i, n))
    best = None
    for hdr, count in cands[:12]:
        # record start: id@+8, coords@+20; try spacing 52..260 step 4
        for base in (hdr + 24, hdr + 28):
            for stride in range(52, 264, 4):
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
                        if bad > 5:
                            break
                if ok >= 40 and bad <= 2:
                    return (hdr, count, base, stride)
    return None

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
res = find_node_section_v2(p)
print("molding1:", res)
if res:
    hdr, count, base, stride = res
    for k in range(3):
        rec = base + k * stride
        print(f"  N{k+1}: id={u32(p, rec+8)} x={d64(p, rec+20):.5g} y={d64(p, rec+28):.5g} z={d64(p, rec+36):.5g}")
