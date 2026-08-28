"""v17 记录族验证: 用 eid@CONST+18 布局解析 Y=2 段, 对比 oracle eid 集合."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, is_const

p = open("output/ground_truth/v17_payload.bin", "rb").read()

# oracle eid 集合
f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); cnt = int(f.readline().split()[1])
gt = set(int(l) for l in f if l.strip())
f.close()

def parse_region(lo, hi, cnt, label):
    """按 family-1 布局解析区域: [CONST][storage][k][701][2596][1][0][EID@+18][0][0][m][flag@+28][rows@+32..0]"""
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
            rows = []
            k = 32
            while u32(p, rec + k) != 0 and len(rows) < 12:
                rows.append(u32(p, rec + k))
                k += 4
            out.append((eid, cfg, tuple(rows), u32(p, rec + 4)))
        j += 1
    return out

# 段 2000146 (Y=2, cnt=1643): sh=30169955, 下一段 sh=30261343
recs = parse_region(30169955, 30261343, 1643, "2000146")
print(f"segment 2000146: {len(recs)} records")
ok_eid18 = sum(1 for r in recs if r[0] in gt)
ok_stor = sum(1 for r in recs if r[3] in gt)
print(f"  eid@+18 in oracle: {ok_eid18}/{len(recs)}")
print(f"  storage@+4 in oracle: {ok_stor}/{len(recs)}")
print("  first 6 (eid, cfg, nrows, storage):", [(r[0], r[1], len(r[2]), r[3]) for r in recs[:6]])
print("  eid range:", min(r[0] for r in recs), "-", max(r[0] for r in recs))
print("  cfg distribution:", {c: sum(1 for r in recs if r[1] == c) for c in set(r[1] for r in recs)})
