"""v17 全局 core 扫描: 不要求 CONST 锚定, 用 (701|686)+2596 模式, 验证 966 缺失元素覆盖率."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, load_payload, find_node_section_struct

p = open("output/ground_truth/v17_payload.bin", "rb").read()

f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()

# ---- row_map 重建 ----
ns_list = []
for ens in find_node_section_struct(p, multi=True):
    if ens[1] >= 50:
        ns_list.append(ens)
row_map = {}
row = 0
for cfg in sorted(ns_list, key=lambda s: s[2]):
    hi, count, base2, stride, idoff, chain = cfg
    for k in range(count):
        rec = base2 + k * stride
        if rec + stride > len(p):
            break
        from decoder import d64
        nid = u32(p, rec + idoff)
        x = d64(p, rec + 12)
        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9):
            break
        row += 1
        row_map[row] = nid
print(f"rows={len(row_map)}")

# ---- 全局 (701|686)+2596 扫描 ----
# 701 在 q (u16 pos): eid = u16(q+8)|u16(q+10)<<16; flag=u32(q+18); rows@q+22
import struct
cores = {}
j = 0
MARK1 = struct.pack("<HH", 701, 2596)
MARK2 = struct.pack("<HH", 686, 2596)
cnt1 = cnt2 = 0
for MARK, tag in ((MARK1, "701"), (MARK2, "686")):
    j = 0
    while True:
        j = p.find(MARK, j)
        if j < 0:
            break
        q = j  # q = 701 位置
        eid = u16(p, q + 8) | (u16(p, q + 10) << 16)
        flag = u32(p, q + 18)
        cfg = flag >> 16
        if 300 <= cfg <= 500 and (flag & 0xFFFF) == 0 and 1 <= eid <= 10_000_000:
            rows = []
            k = q + 22
            while u32(p, k) != 0 and len(rows) < 20:
                rows.append(u32(p, k))
                k += 4
            if 1 <= len(rows) <= 20 and all(1 <= r <= len(row_map) for r in rows):
                if eid not in cores:
                    cores[eid] = (cfg - 256, tuple(rows), q)
                if tag == "701":
                    cnt1 += 1
                else:
                    cnt2 += 1
        j += 2
print(f"core hits: 701={cnt1} 686={cnt2} unique eids={len(cores)}")
print(f"cores in gt: {sum(1 for e in cores if e in gt)}")
missing = gt - set(cores)
print(f"missing after scan: {len(missing)}")
ms = sorted(missing)
if ms:
    runs = []
    start = prev = ms[0]
    for v in ms[1:]:
        if v == prev + 1:
            prev = v
        else:
            runs.append((start, prev)); start = prev = v
    runs.append((start, prev))
    print("missing runs:", runs[:20])

# ---- 抽查: 已知 oracle 元素 ----
# eid=131694 config=60 nodes=3462253 3462254; eid=131684 config=60 nodes=2996947 2996948 2000000
for eid, onodes in [(131694, [3462253, 3462254]),
                    (131684, [2996947, 2996948, 2000000]),
                    (131508, [2991373, 2980505]),
                    (131633, [2911530, 2911535, 2911536, 2911553]),
                    (589001, [717301, 741336]),
                    (589100, [617751, 617756, 617752, 617757]),
                    (131766, [617771]),
                    (589700, [753656, 758015]),
                    (263827, [219546, 220347, 220624, 219550])]:
    c = cores.get(eid)
    if c is None:
        print(f"eid={eid}: NOT FOUND")
        continue
    config, rows, q = c
    nds = [row_map.get(r, r) for r in rows]
    match = "OK" if sorted(nds) == sorted(onodes) else "MISMATCH"
    print(f"eid={eid} config={config} rows={list(rows)} nodes={nds} oracle={onodes} {match}")

# ---- SHORT 段中 +4 值是否即 eid (config 104 段) ----
# seg 100026: +4=144234, oracle config=104 nodes=433859 433860 433857 433856
for r in (3117, 3118, 3119, 3120):
    print(f"  row {r} -> nid {row_map.get(r)}")
