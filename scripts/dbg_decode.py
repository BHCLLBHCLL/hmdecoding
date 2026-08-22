
import sys, traceback
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, find_node_section_struct

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
ns = find_node_section(p)
ns_list = []
nodes = {}
if ns:
    n1, b1 = parse_nodes(p, ns)
    print("n1:", len(n1), "ns:", ns)
    if len(n1) >= max(10, ns[1] * 0.85):
        nodes = n1
        ns_list.append(ns)
    print("branch1 ns_list:", ns_list)
if len(nodes) < 10:
    print("entering struct multi...")
    for ens in find_node_section_struct(p, multi=True):
        n2, b2 = parse_nodes(p, ens)
        if n2:
            nodes.update(n2)
            ns_list.append(ens)
print("ns_list:", [(len(x), x) for x in ns_list])
for cfg in sorted(ns_list, key=lambda s: s[2]):
    print("cfg:", cfg, "len:", len(cfg))
    hi, count, base2, stride, idoff, chain = cfg[0], cfg[1], cfg[3], cfg[4], cfg[5]
    print("  unpack ok")
