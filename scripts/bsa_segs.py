
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import decode_elements
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\body_side_assembly.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = {k+1: u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
print("body_side_assembly segs:", len(segs), "Y dist:", __import__('collections').Counter(s[4] for s in segs).most_common())
print("cnt total:", sum(s[3] for s in segs), "ns:", ns[1])
