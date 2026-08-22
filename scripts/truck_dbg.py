
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, row_map_from_nodes
from decoder import _parse_a_type, CONST

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = row_map_from_nodes(p, ns, base)
sh = 21436728
s = sh + 24
print("s:", s, "CONST:", u32(p, s) == CONST)
nxt = None
for j in range(s + 24, s + 300):
    if u32(p, j) == CONST:
        nxt = j; break
print("next CONST:", nxt, "stride:", nxt - s if nxt else None)
got = _parse_a_type(p, sh, 188, ns[1], rm, max_rec=3)
print("parse:", "OK" if got else "FAIL")
