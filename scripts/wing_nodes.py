
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
ns = find_node_section(p)
print("node section:", ns)
if ns:
    nodes, base = parse_nodes(p, ns)
    print("nodes:", len(nodes))
    ids = [u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])]
    print("node ids first:", ids[:5], "count:", len(ids))
    id2row = {nid: k+1 for k, nid in enumerate(ids)}
    print("row of 1569:", id2row.get(1569), "1571:", id2row.get(1571), "1566:", id2row.get(1566), "1567:", id2row.get(1567))
