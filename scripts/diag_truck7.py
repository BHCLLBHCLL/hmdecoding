"""truck 各段覆盖统计: 找 partial 段."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, parse_nodes, find_elem_segments, _parse_a_type

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

segs = find_elem_segments(p)
partial = []
total_miss = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if got is None:
        total_miss += cnt
        partial.append((segid, cnt, 0, Y))
    elif len(got) < cnt:
        total_miss += cnt - len(got)
        partial.append((segid, cnt, len(got), Y))
partial.sort(key=lambda x: -(x[1] - x[2]))
print(f"partial/none segs: {len(partial)}, total miss: {total_miss}")
for pseg in partial[:20]:
    print("  ", pseg)
