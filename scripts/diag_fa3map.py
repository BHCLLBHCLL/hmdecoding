"""frame_assembly_3 eid 映射诊断: 段结构 + 缺失/多余 eid 关系."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, _parse_a_type

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_3.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
segs = find_elem_segments(p)
print("nodes:", len(n1), "segs:", len(segs))
print("X:", Counter(s[4] for s in segs), "Y:", Counter(s[5] for s in segs).most_common(10))
print("cfg71:", Counter(s[2] for s in segs).most_common(10))
for s in segs:
    print("  seg:", s)

lines = open("output/ground_truth/fa3_elemids.txt").read().splitlines()
gt = set(int(l) for l in lines[3:] if l.strip())

# 逐段解析
dec = {}
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    n = len(got) if got else 0
    print(f"seg {segid} Y={Y} cnt={cnt} -> {n}")
    if got:
        dec.update(got)

missing = sorted(gt - set(dec))
extra = sorted(set(dec) - gt)
print(f"\noracle {len(gt)} decoded {len(dec)}")
print(f"missing {len(missing)}: {missing[:20]} ... {missing[-5:]}")
print(f"extra {len(extra)}: {extra[:20]} ... {extra[-5:]}")
