
import sys, time
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64, find_node_section_struct, parse_nodes, decode_elements

log = open("output/ground_truth/v17_elem_full.txt", "w")
def T(m, t0):
    log.write(f"{m}: {time.time()-t0:.1f}s\n"); log.flush()

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
t0 = time.time()
ns_list = []
nodes = {}
for ens in find_node_section_struct(p, multi=True):
    if ens[1] < 50: continue
    n2, b2 = parse_nodes(p, ens)
    if n2:
        nodes.update(n2)
        ns_list.append(ens)
T(f"nodes: {len(nodes)}", t0)
row_map = {}
row = 0
for cfg in sorted(ns_list, key=lambda s: s[2]):
    hi, count, base2, stride, idoff, chain = cfg
    for k in range(count):
        rec = base2 + k * stride
        if rec + stride > len(p): break
        nid = u32(p, rec + idoff)
        x = d64(p, rec + 12)
        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9): break
        row += 1
        row_map[row] = nid
T("row_map done", t0)
t0 = time.time()
elems = decode_elements(p, row_map, len(nodes), max_rec=None)
T(f"elements full: {len(elems) if elems else 0}", t0)
log.close()
