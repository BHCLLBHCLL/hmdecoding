
import sys, time
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, row_map_from_nodes, find_elem_segments, decode_elements, _parse_ws_variant_b

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
t0 = time.time()
ns = find_node_section(p)
print(f"find_node_section: {time.time()-t0:.1f}s -> {ns}")
t0 = time.time()
nodes, base = parse_nodes(p, ns)
print(f"parse_nodes: {time.time()-t0:.1f}s -> {len(nodes)}")
t0 = time.time()
rm = row_map_from_nodes(p, ns, base)
segs = find_elem_segments(p)
print(f"find_elem_segments: {time.time()-t0:.1f}s -> {len(segs)} segs")
t0 = time.time()
elems = decode_elements(p, rm, ns[1])
print(f"decode_elements: {time.time()-t0:.1f}s -> {len(elems) if elems else 0}")
