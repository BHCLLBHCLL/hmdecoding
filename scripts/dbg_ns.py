
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
ns = find_node_section(p)
print("ns:", ns, "len:", len(ns) if ns else None)
n1, b1 = parse_nodes(p, ns)
print("n1:", len(n1))
# mimic decode branch
ns_list = []
nodes = {}
if ns:
    if len(n1) >= max(10, ns[1] * 0.85):
        nodes = n1
        ns_list.append(ns)
print("ns_list after branch:", [(len(x), x) for x in ns_list])
