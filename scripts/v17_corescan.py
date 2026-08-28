"""v17 全载荷 family-1 core 扫描: 所有 CONST 记录按 flag@+28 解析, 对比 oracle 全集."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, is_const, find_node_section_struct

p = open("output/ground_truth/v17_payload.bin", "rb").read()

f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()
print("oracle elems:", len(gt))

MARK = b"\xf5\x1f\x24\x70"
cores = {}
dup = 0
j = 0
while True:
    j = p.find(MARK, j)
    if j < 0:
        break
    flag = u32(p, j + 28)
    cfg = flag >> 16
    if 300 <= cfg <= 500 and (flag & 0xFFFF) == 0:
        eid = u32(p, j + 18)
        rows = []
        k = j + 32
        while u32(p, k) != 0 and len(rows) < 12:
            rows.append(u32(p, k))
            k += 4
        if 1 <= len(rows) <= 12 and all(1 <= r <= 354175 for r in rows):
            if eid in cores and cores[eid] != (cfg, tuple(rows)):
                dup += 1
            cores[eid] = (cfg, tuple(rows))
    j += 1
print(f"family-1 cores found: {len(cores)} (conflicting dup: {dup})")
in_gt = sum(1 for e in cores if e in gt)
print(f"core eids in oracle: {in_gt}, not in oracle: {len(cores) - in_gt}")
missing = gt - set(cores)
print(f"oracle eids NOT covered by cores: {len(missing)}")
print("  sample missing:", sorted(missing)[:20])

# 配置分布
from collections import Counter
cc = Counter(c[0] - 256 for c in cores.values())
print("config distribution (top):", cc.most_common(15))

# B型段检查: X=2 段是否存在
from decoder import find_elem_segments
segs = find_elem_segments(p)
x2 = [s for s in segs if s[4] == 2]
x3 = [s for s in segs if s[4] == 3]
print(f"\nsegments: X=2: {len(x2)} (sum_cnt={sum(s[3] for s in x2)}), X=3: {len(x3)} (sum_cnt={sum(s[3] for s in x3)})")

# X=3 段中 Y=2 与 Y!=2 的 cnt 分布
y2 = [s for s in x3 if s[5] == 2]
yn2 = [s for s in x3 if s[5] != 2]
print(f"X=3: Y=2 {len(y2)} segs sum_cnt={sum(s[3] for s in y2)}, Y!=2 {len(yn2)} segs sum_cnt={sum(s[3] for s in yn2)}")

# 每个 X=3 Y=2 段: core 覆盖情况 (取前 5 段 + 全部汇总)
segs_sorted = sorted(x3, key=lambda s: s[0])
tot_ok = 0
for idx, (sh, segid, cfg71, cnt, X, Y) in enumerate(segs_sorted):
    hi = segs_sorted[idx + 1][0] if idx + 1 < len(segs_sorted) else len(p)
    n = 0
    j = sh
    while True:
        j = p.find(MARK, j, hi)
        if j < 0:
            break
        flag = u32(p, j + 28)
        c = flag >> 16
        if 300 <= c <= 500 and (flag & 0xFFFF) == 0:
            eid = u32(p, j + 18)
            if eid in gt:
                n += 1
        j += 1
    tot_ok += n
    if Y == 2 and n != cnt and idx < 200:
        print(f"  Y=2 seg {segid} cnt={cnt} cores_in_gt={n}")
print(f"total cores-in-gt within X=3 regions: {tot_ok}")
