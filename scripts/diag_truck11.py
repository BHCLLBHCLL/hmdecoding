"""truck 解码 eid vs oracle 全量对比, 定位缺失 eid."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments, _parse_a_type

# oracle
lines = open("output/ground_truth/truck_elemids.txt").read().splitlines()
gt = set(int(l) for l in lines[3:] if l.strip())
print(f"oracle: {len(gt)}")

# 解码
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
segs = find_elem_segments(p)
dec = {}
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if got:
        dec.update(got)
print(f"decoded: {len(dec)}")

missing = gt - set(dec)
extra = set(dec) - gt
print(f"missing: {len(missing)} extra: {len(extra)}")
ms = sorted(missing)
# 缺失 eid 区间
runs = []
if ms:
    start = prev = ms[0]
    for v in ms[1:]:
        if v == prev + 1:
            prev = v
        else:
            runs.append((start, prev)); start = prev = v
    runs.append((start, prev))
print(f"missing runs: {len(runs)}")
for a, b in runs[:20]:
    print(f"  {a}..{b} ({b-a+1})")
print("extra sample:", sorted(extra)[:10])
