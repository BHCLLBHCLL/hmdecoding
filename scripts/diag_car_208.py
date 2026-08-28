"""car_section: 找 config 208/206 来源段."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, _parse_a_type

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/car_section.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
rc = len(row_map)

segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    r = _parse_a_type(p, sh, cnt, rc, row_map)
    if not r:
        continue
    bad = {e: (c, n) for e, (c, n) in r.items() if c in (208, 206)}
    if bad:
        print(f"segid={segid} cnt={cnt} Y={Y}: {len(bad)} config208/206, sample={list(bad.items())[:3]}")
