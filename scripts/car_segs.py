
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, find_elem_segments
from decoder import decode_elements

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\car_section.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = {k+1: u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
print("segs:", len(segs))
from collections import Counter
total = 0; decoded = 0
fails = []
for sh, segid, cfg71, cnt, X, Y in segs:
    got = decode_elements(p, rm, len(nodes))
    break
# run per-seg via decode_elements internals is complex; use a simpler per-seg decode
def seg_delta(sh, cnt, X, Y):
    # single seg decode through decode_elements is not per-seg; approximate via parsing
    pass
# Just print Y distribution and counts
print("Y dist:", dict(Counter(s[4] for s in segs)))
print("cnt total:", sum(s[3] for s in segs))
