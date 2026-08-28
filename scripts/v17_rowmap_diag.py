"""v17 row_map 错位诊断: 定位 -1 偏移起点, 检查 2000000 节点与缺失节点."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section_struct

p = open("output/ground_truth/v17_payload.bin", "rb").read()

# oracle 节点表
f = open("output/ground_truth/v17gt_dummy_nodeids.txt")
f.readline(); f.readline()
gtn = set(int(l) for l in f if l.strip())
f.close()
print(f"oracle nodes={len(gtn)} 2000000 in oracle: {2000000 in gtn} 3481964: {3481964 in gtn} 3481965: {3481965 in gtn}")

# 重建 row_map 与各段信息
ns_list = []
for ens in find_node_section_struct(p, multi=True):
    if ens[1] >= 50:
        ns_list.append(ens)
row_map = {}
row = 0
seg_of_row = {}
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
        seg_of_row[row] = (base2, stride, idoff)

# nid -> row 反查
row_of = {v: k for k, v in row_map.items()}
print(f"rows={len(row_map)} unique nids={len(row_of)}")

# 关键 nid 的行号
for nid in (219545, 219546, 220346, 220347, 220623, 220624, 219549, 219550,
            2996947, 2996948, 2000000, 3462253, 3462254, 3481963, 3481966):
    print(f"  nid {nid}: row={row_of.get(nid)}")

# row 151675..151690 与 50935..50945 的 nid 序列
for lo, hi in ((151675, 151690), (50935, 50945)):
    print(f"rows {lo}..{hi}: {[row_map.get(r) for r in range(lo, hi+1)]}")

# 段边界检查: row 151679 属于哪个段, 该段行范围
seg = seg_of_row.get(151679)
print(f"row 151679 seg: base={seg[0]} stride={seg[1]} idoff={seg[2]}")
# 该段所有行
rows_in_seg = [r for r, s in seg_of_row.items() if s == seg]
print(f"  seg rows: {min(rows_in_seg)}..{max(rows_in_seg)} nids: {row_map[min(rows_in_seg)]}..{row_map[max(rows_in_seg)]}")
# 段内 nid 是否连续
nids_seg = [row_map[r] for r in sorted(rows_in_seg)]
gaps = [(a, b) for a, b in zip(nids_seg, nids_seg[1:]) if b != a + 1]
print(f"  nid gaps in seg: {gaps[:10]} (total {len(gaps)})")

# 全局: row_map 里 nid 不连续的点 (前 20)
items = sorted(row_map.items())
prev_nid = None
disc = []
for r, nid in items:
    if prev_nid is not None and nid != prev_nid + 1:
        disc.append((r, prev_nid, nid))
    prev_nid = nid
print(f"nid discontinuities (row, prev, cur): {disc[:20]} total={len(disc)}")
