"""truck 逐段 eid 覆盖: 用当前 _parse_a_type 逻辑逐段解码, 看缺失 212715+ 在哪个段."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, d64, find_node_section, parse_nodes,
                     find_elem_segments, is_const, _parse_a_type, decode)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
segs = find_elem_segments(p)
lines = open("output/ground_truth/truck_elemids.txt").read().splitlines()
gt = set(int(l) for l in lines if l.strip().isdigit())

# 对每个段用 _parse_a_type 解码, 报告 eid 范围 和 命中缺失(212715+) 数
miss_lo, miss_hi = 212715, 228633
print("=== 逐段 (仅 Y!=1 且 cnt>0) ===")
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if not got:
        print(f"seg {segid} Y={Y} cnt={cnt} -> None")
        continue
    eids = sorted(got)
    hit = [e for e in eids if miss_lo <= e <= miss_hi]
    lo, hi = eids[0], eids[-1]
    if hit or Y in (4, 7):
        print(f"seg {segid} Y={Y} cnt={cnt} -> {len(got)} eids[{lo}..{hi}] hit_high={len(hit)}")

# 汇总: 缺失 eid 区间
m = decode(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
missing = sorted(gt - set(m.elements.keys()))
ranges = []
for v in missing:
    if ranges and v == ranges[-1][1]+1:
        ranges[-1][1] = v
    else:
        ranges.append([v, v])
print("\n缺失区间:", ranges)
print("缺失总数:", len(missing))
