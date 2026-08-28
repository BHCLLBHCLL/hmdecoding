"""v17 定位 row_map 重复行 + 缺失节点 3481964/3481965 的存储位置."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section_struct, find_node_section

p = open("output/ground_truth/v17_payload.bin", "rb").read()

ns_list = []
for ens in find_node_section_struct(p, multi=True):
    if ens[1] >= 50:
        ns_list.append(ens)
row_map = {}
row = 0
row_seg = {}
for cfg in sorted(ns_list, key=lambda s: s[2]):
    hi, count, base2, stride, idoff, chain = cfg
    for k in range(count):
        rec = base2 + k * stride
        if rec + stride > len(p):
            break
        nid = u32(p, rec + idoff)
        x = d64(p, rec + 12)
        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9):
            break
        row += 1
        row_map[row] = nid
        row_seg[row] = (base2, stride, idoff, k)

# 1) 重复 nid
from collections import defaultdict
rows_of = defaultdict(list)
for r, nid in row_map.items():
    rows_of[nid].append(r)
dups = {n: rs for n, rs in rows_of.items() if len(rs) > 1}
print("duplicate nids:", dups)

# 2) rows 116660..116745 详情
print("\nrows 116660..116745:")
for r in range(116660, 116746):
    seg = row_seg.get(r)
    print(f"  row {r}: nid={row_map.get(r)} seg_base={seg[0] if seg else None} stride={seg[1] if seg else None} k={seg[3] if seg else None}")

# 3) rows 36388..36412
print("\nrows 36388..36412:")
for r in range(36388, 36413):
    seg = row_seg.get(r)
    print(f"  row {r}: nid={row_map.get(r)} seg_base={seg[0] if seg else None} stride={seg[1] if seg else None} k={seg[3] if seg else None}")

# 4) 搜索 3481964/3481965 的 u32 出现位置
for nid in (3481964, 3481965):
    pat = struct.pack("<I", nid)
    pos = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        pos.append(j)
        j += 1
    print(f"\nnid {nid}: {len(pos)} hits: {pos[:20]}")
    for q in pos[:8]:
        # 显示上下文, 判断是否在节点记录里 (前后有 double 坐标)
        ctx = []
        for off in (-16, -12, -8, -4, 0, 4, 8, 12, 16, 20, 24):
            v = u32(p, q + off)
            ctx.append(f"{off:+d}:{v}")
        print(f"  @{q}: {' '.join(ctx)}")
