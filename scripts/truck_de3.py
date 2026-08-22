
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, row_map_from_nodes, decode_elements

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = row_map_from_nodes(p, ns, base)
print("ns:", ns)
elems = decode_elements(p, rm, ns[1])
print("decode_elements:", len(elems) if elems else 0)
# WS-B check
from decoder import _parse_ws_variant_b
wb = _parse_ws_variant_b(p, rm, ns[1])
print("WS-B:", len(wb) if wb else 0)
