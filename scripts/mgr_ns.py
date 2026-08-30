
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, find_node_section_struct, parse_nodes
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
ns = find_node_section(p)
print("ns:", ns)
if ns:
    n1, b1 = parse_nodes(p, ns)
    print("ns parse:", len(n1))
segs = find_node_section_struct(p, multi=True)
print("struct segs:", len(segs))
tot = 0
for s in segs:
    n2, b2 = parse_nodes(p, s)
    tot += len(n2)
    print("  seg:", s[1], "base:", s[2], "stride:", s[3], "n:", len(n2))
print("struct total:", tot)
