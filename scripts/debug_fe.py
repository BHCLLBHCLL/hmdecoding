
import sys, json
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes

CONST = 0x70241FF5

# fe_only chain debug
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\fe_only.hm")
ns = find_node_section(p)
hdr, ncount, shift, idoff, coordoff = ns[0]
nodes, base = parse_nodes(p, hdr, ncount, shift, idoff, coordoff)
ids = [u32(p, base + k * 52 + idoff) for k in range(ncount)]
row_map = {k + 1: nid for k, nid in enumerate(ids)}
s = 4748145 + 24
rec = s; eid = 191098
for k in range(5):
    nds = [u32(p, rec + 10 + j * 4) for j in range(8)]
    ids8 = [row_map.get(r) for r in nds]
    nxt = None
    for j in range(rec + 42 + 4, rec + 400):
        if u32(p, j) == 0 and u32(p, j + 4) == 0 and 300 <= u16(p, j + 8) <= 500:
            nxt = j; break
    stride = nxt - rec if nxt else None
    ne = None
    if nxt:
        for z in range(rec + stride - 4, rec + 42 - 2, -2):
            v = u16(p, z)
            if v != 0 and u16(p, z + 2) == 0:
                ne = v; break
    print(f"k={k} eid={eid} nds8={ids8[:3]}... nxt={nxt} ne={ne}")
    gt = json.load(open("output/ground_truth/multi_elem_gt.json"))["fe_only.hm"]["elems"]
    g = gt.get(str(eid))
    if g:
        exp = [x for x in g["nodes"] if x]
        print(f"    GT eid={eid}: nodes[:3]={exp[:3]} match={ids8[:len(exp)] == exp}")
    eid = ne if eid < 65536 else (eid & 0xFFFF0000) | ne
    rec = nxt
