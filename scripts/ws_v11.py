
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes

p = load_payload("WS_3.2_3d_tetra_finish.hm")
ns = find_node_section(p)
print("find_node_section(WS) ->", ns)
if ns:
    nodes, base = parse_nodes(p, ns)
    print("parsed nodes:", len(nodes), "first ids:", sorted(list(nodes.keys()))[:5], "last:", sorted(list(nodes.keys()))[-3:])
