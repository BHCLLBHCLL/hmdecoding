"""v17 SHORT 段区域 family-1 解析验证."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, is_const

p = open("output/ground_truth/v17_payload.bin", "rb").read()

f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()

def parse_region(lo, hi):
    out = []
    j = lo + 24
    while True:
        j = p.find(b"\xf5\x1f", j, hi)
        if j < 0:
            break
        if is_const(u32(p, j)):
            rec = j
            eid = u32(p, rec + 18)
            flag = u32(p, rec + 28)
            cfg = flag >> 16
            low = flag & 0xFFFF
            rows = []
            k = 32
            while u32(p, rec + k) != 0 and len(rows) < 12:
                rows.append(u32(p, rec + k))
                k += 4
            out.append((eid, cfg, low, tuple(rows), u32(p, rec + 4)))
        j += 1
    return out

CASES = [
    (44267255, 44284291, 300001, 3),      # Y=7 SHORT
    (31997647, 31998339, 2000486, 4),     # Y=5 SHORT
    (40564251, 40564463, 100026, 1),      # Y=9 SHORT cnt=1
    (38005415, 38019435, 6500113, 125),   # Y=7 "OK" (可疑)
    (65225749, 65233945, 800029, 73),     # Y=7 "OK" (可疑)
]
for lo, hi, segid, cnt in CASES:
    recs = parse_region(lo, hi)
    n = len(recs)
    ok = sum(1 for r in recs if r[0] in gt)
    flagok = sum(1 for r in recs if 300 <= r[1] <= 500 and r[2] == 0)
    print(f"\nsegment {segid} (cnt={cnt}): records={n} eid@+18 in oracle={ok} flag@+28 valid={flagok}")
    for r in recs[:5]:
        print(f"   eid={r[0]} cfg={r[1]} low={r[2]} rows={list(r[3])} storage={r[4]}")
