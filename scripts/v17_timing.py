
import sys, time
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, row_map_from_nodes, find_elem_segments, decode_elements

log = open("output/ground_truth/v17_timing.txt", "w")
def T(msg, t0):
    log.write(f"{msg}: {time.time()-t0:.1f}s\n")
    log.flush()

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
t0 = time.time()
ns = find_node_section(p)
T("find_node_section", t0)
log.write(f"ns={ns}\n"); log.flush()
t0 = time.time()
nodes, base = parse_nodes(p, ns)
T("parse_nodes", t0)
log.write(f"nodes={len(nodes)} count={ns[1]}\n"); log.flush()
t0 = time.time()
rm = row_map_from_nodes(p, ns, base)
T("row_map", t0)
t0 = time.time()
segs = find_elem_segments(p)
T("find_elem_segments", t0)
log.write(f"segs={len(segs)}\n"); log.flush()
t0 = time.time()
elems = decode_elements(p, rm, ns[1], max_rec=2000)
T("decode_elements", t0)
log.write(f"elems={len(elems) if elems else 0}\n")
log.close()
