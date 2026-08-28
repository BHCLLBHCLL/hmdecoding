"""v17 分析 966 缺失元素: SHORT 段 +4 值 / 嵌入 core eid 与缺失集合的对应关系."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, is_const, find_node_section_struct, find_elem_segments

p = open("output/ground_truth/v17_payload.bin", "rb").read()

f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()

# cores (CONST 锚定)
MARK = b"\xf5\x1f\x24\x70"
cores = {}
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
            cores[eid] = (cfg, tuple(rows))
    j += 1

missing = gt - set(cores)
print(f"missing: {len(missing)}")
for v in (144234, 365000, 365001, 365002, 263874, 517663, 589141, 589209, 131704, 64921, 589271):
    print(f"  eid {v}: in_missing={v in missing}, in_cores={v in cores}")

# 缺失 eid 分布
ms = sorted(missing)
runs = []
start = prev = ms[0]
for v in ms[1:]:
    if v == prev + 1:
        prev = v
    else:
        runs.append((start, prev))
        start = prev = v
runs.append((start, prev))
print(f"\nmissing runs: {len(runs)}")
for a, b in runs[:40]:
    print(f"  {a}..{b} ({b-a+1})")

# SHORT 段分析: 每段提取 +4 值 与 嵌入 core (·,701/686 标记)
segs = sorted(find_elem_segments(p), key=lambda s: s[0])
short = [s for s in segs if s[5] != 2]
print(f"\nSHORT segs: {len(short)}")
ref4_all = []
core_eids_all = []
for idx, (sh, segid, cfg71, cnt, X, Y) in enumerate(short):
    # 区域边界: 下一个段头
    hi = len(p)
    for s2 in segs:
        if s2[0] > sh:
            hi = s2[0]
            break
    # 段内 const 记录
    refs = []
    core_eids = []
    j = sh
    while True:
        j = p.find(MARK, j, hi)
        if j < 0:
            break
        if is_const(u32(p, j)):
            refs.append(u32(p, j + 4))
            # 嵌入 core: 找 (·,701) 或 (·,686) 标记后接 (2596,·)
            for off in range(8, 400, 4):
                v = u16(p, j + off + 2)
                if v in (701, 686) and u16(p, j + off + 4) == 2596:
                    c0 = j + off - 8
                    ceid = u32(p, c0 + 18)
                    cflag = u32(p, c0 + 28)
                    core_eids.append((ceid, cflag >> 16))
                    break
        j += 1
    ref4_all += refs
    core_eids_all += core_eids
    if idx < 12:
        print(f"  seg {segid} Y={Y} cnt={cnt}: +4={refs[:6]} cores={core_eids[:6]}")

print(f"\nSHORT +4 values total: {len(ref4_all)}")
print(f"  +4 in missing: {sum(1 for v in ref4_all if v in missing)}")
print(f"  +4 in gt: {sum(1 for v in ref4_all if v in gt)}")
print(f"  +4 not in gt: {sum(1 for v in ref4_all if v not in gt)}")
print(f"SHORT core eids total: {len(core_eids_all)}")
print(f"  cores in missing: {sum(1 for e, _ in core_eids_all if e in missing)}")
print(f"  cores in cores(CONST): {sum(1 for e, _ in core_eids_all if e in cores)}")
print(f"  cores not in gt: {sum(1 for e, _ in core_eids_all if e not in gt)}")
from collections import Counter
print("  core flag distribution:", Counter(c for _, c in core_eids_all).most_common(10))
