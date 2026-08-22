
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes

CONST = 0x70241FF5
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\clip_refine.hm")
ns = find_node_section(p)
hdr, ncount, shift, idoff, coordoff = ns[0]
nodes, base = parse_nodes(p, hdr, ncount, shift, idoff, coordoff)
ids = [u32(p, base + k * 52 + idoff) for k in range(ncount)]
row_map = {k + 1: nid for k, nid in enumerate(ids)}
print("node ids first/last:", ids[:5], ids[-3:], "count:", ncount)

sh = 972751
s = sh + 24
print("stream at", s, "CONST:", hex(u32(p, s)))
stride = None
for j in range(s + 24, s + 200):
    if u32(p, j) == CONST:
        stride = j - s
        break
print("stride:", stride)
target = (104 + 256) << 16
fp = None
for off in range(12, stride - 12, 4):
    if u32(p, s + off) == target:
        fp = off
        break
print("flag_pos:", fp, hex(target))
n = (stride - (fp + 4) - 8) // 4
print("n:", n)
for k in range(5):
    rec = s + k * stride
    eid = u32(p, rec + 4)
    nds = [u32(p, rec + fp + 4 + j * 4) for j in range(n)]
    print(f"  rec{k}: eid={eid} rows={nds} ids={[row_map.get(r) for r in nds]}")
gt = json.load(open("output/ground_truth/multi_elem_gt.json"))["clip_refine.hm"]
print("GT E1:", gt["elems"]["1"])
