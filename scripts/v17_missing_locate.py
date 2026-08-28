"""v17 剩余 359 缺失元素定位: 搜索 eid 在 payload 中的出现位置与上下文."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, find_node_section_struct, find_elem_segments

p = open("output/ground_truth/v17_payload.bin", "rb").read()
f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()

# 全局 core 扫描 (与 v17_global_core 相同)
MARK1 = struct.pack("<HH", 701, 2596)
cores = {}
j = 0
while True:
    j = p.find(MARK1, j)
    if j < 0:
        break
    q = j
    eid = u16(p, q + 8) | (u16(p, q + 10) << 16)
    flag = u32(p, q + 18)
    cfg = flag >> 16
    if 300 <= cfg <= 500 and (flag & 0xFFFF) == 0 and 1 <= eid <= 10_000_000:
        k = q + 22
        rows = []
        while u32(p, k) != 0 and len(rows) < 20:
            rows.append(u32(p, k)); k += 4
        if 1 <= len(rows) <= 20 and all(1 <= r <= 354175 for r in rows):
            cores.setdefault(eid, (cfg - 256, tuple(rows)))
    j += 2
missing = sorted(gt - set(cores))
print(f"missing: {len(missing)}")

# 段映射: 位置 -> 段
segs = sorted(find_elem_segments(p), key=lambda s: s[0])
def seg_of(pos):
    cur = None
    for s in segs:
        if s[0] <= pos:
            cur = s
        else:
            break
    return cur

# 每个缺失 eid 的 u32 出现位置
from collections import Counter
seg_cnt = Counter()
samples = {}
for eid in missing:
    pat = struct.pack("<I", eid)
    pos = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        pos.append(j); j += 1
    for q in pos:
        s = seg_of(q)
        key = (s[1], s[5]) if s else ("none", -1)
        seg_cnt[key] += 1
    if pos:
        samples.setdefault(eid, pos)
print("\nhit segment distribution (segid, Y): count")
for k, v in seg_cnt.most_common(30):
    print(f"  seg={k[0]} Y={k[1]}: {v}")
print(f"\neids with no u32 hit: {sum(1 for e in missing if e not in samples)}")

# 代表性 eid 上下文 dump
for eid in (131508, 131633, 131766, 589001, 589100, 589700, 589136, 131684, 131764):
    pos = samples.get(eid)
    if not pos:
        print(f"\neid={eid}: NO HIT")
        continue
    print(f"\neid={eid}: {len(pos)} hits {[q for q in pos[:6]]}")
    for q in pos[:3]:
        s = seg_of(q)
        print(f"  @{q} seg={s[1] if s else '?'} Y={s[5] if s else '?'}  rel={q - s[0] if s else '?'}")
        for off in range(-12, 36, 4):
            v = u32(p, q + off)
            u = (u16(p, q + off), u16(p, q + off + 2))
            print(f"    {off:+4d}: {p[q+off:q+off+4].hex(' ')}  u32={v:<10d} u16={u}")
