
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, find_elem_segments, decode_elements
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\car_section.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = {k+1: __import__('struct').unpack_from('<I', p, base + k*ns[3] + ns[4])[0] for k in range(ns[1])}
recs = decode_elements(p, rm, len(nodes))
print("decode_elements records:", len(recs) if recs else 0)
from collections import Counter
eidc = Counter(r[0] for r in recs)
dups = {e: n for e, n in eidc.items() if n > 1}
print("eid dup in records:", len(dups), "extra:", sum(n-1 for n in dups.values()))
