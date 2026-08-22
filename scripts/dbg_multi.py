
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, find_node_section_struct

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
ns = find_node_section(p)
print("find_node_section:", ns)
if ns:
    n1, b1 = parse_nodes(p, ns)
    print("parse nodes:", len(n1))
extra = find_node_section_struct(p, multi=True)
print("struct multi:", len(extra))
for e in extra[:5]:
    print("  seg:", e, "len:", len(e))
