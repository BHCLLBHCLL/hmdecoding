"""v17 元素记录定位: 通过 oracle 节点 ID 的行号在载荷中定位元素记录.
载荷缓存到 output/ground_truth/v17_payload.bin 避免反复解压."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section_struct, parse_nodes

CACHE = "output/ground_truth/v17_payload.bin"
import os
if os.path.exists(CACHE):
    p = open(CACHE, "rb").read()
else:
    p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
    open(CACHE, "wb").write(p)
print("payload:", len(p))

# 节点段 + row_map
ns_list = []
for ens in find_node_section_struct(p, multi=True):
    if ens[1] < 50:
        continue
    ns_list.append(ens)
row_map = {}
row_of = {}
row = 0
for cfg in sorted(ns_list, key=lambda s: s[2]):
    hi, count, base2, stride, idoff, chain = cfg
    for k in range(count):
        rec = base2 + k * stride
        nid = u32(p, rec + idoff)
        row += 1
        row_map[row] = nid
        row_of[nid] = row
print("rows:", row, "segs:", [(c[2], c[1], c[3]) for c in ns_list])

# oracle 元素: (eid, nodes) — 在载荷中按行号序列搜索
CASES = [
    (365000, [701993, 702237, 701994, 702241]),   # segid=300001 Y=7 SHORT
    (144234, [427020, 427063, 425991, 425983]),   # segid=100026 Y=9 SHORT
    (3912279, None),                               # segid=2000486 Y=5 SHORT (config 60?)
    (1, [2006765, 2129498, 2129497, 2129500]),    # 低 id 缺失
    (100000, [3127953, 3332305, 3127764, 3127776, 3127954, 3332306, 3127766, 3127778]),  # config 208
]
for eid, nodes in CASES:
    print(f"\n== eid={eid}")
    # eid u32 出现位置
    pat = struct.pack("<I", eid)
    hits = []
    start = 0
    while True:
        i = p.find(pat, start)
        if i < 0:
            break
        hits.append(i)
        start = i + 1
        if len(hits) > 8:
            break
    print(f"  eid u32 hits: {hits}")
    if nodes:
        rows = [row_of.get(n) for n in nodes]
        print(f"  node rows: {rows}")
        # 搜索行号 u32 序列 (前 3 个)
        seq = b"".join(struct.pack("<I", r) for r in rows[:3] if r)
        if seq:
            j = p.find(seq)
            print(f"  row-seq u32 hit: {j}")
        # 搜索行号 u16 序列
        seq16 = b"".join(struct.pack("<H", r) for r in rows[:4] if r and r < 65536)
        if seq16:
            j = p.find(seq16)
            print(f"  row-seq u16 hit: {j}")
