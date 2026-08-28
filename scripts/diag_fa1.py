"""诊断 frame_assembly_1.hm 元素 miss 92."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments, _parse_a_type, _parse_v13_elems

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly_1.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
segs = find_elem_segments(p)
print("nodes:", len(n1), "segs:", len(segs))
print("X:", Counter(s[4] for s in segs), "Y:", Counter(s[5] for s in segs).most_common(8))
tot = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    n = len(got) if got else 0
    tot += n
    if got is None or n < cnt:
        print(f"  seg {segid} Y={Y} cnt={cnt} -> {n}")
print("total:", tot)
