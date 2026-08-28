"""SEAT_MODEL: 对比 eid@+4 (存储) vs eid@+18 (family-1) 与 oracle 匹配率."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const

lines = open("output/ground_truth/seatmodel_elemids.txt").read().splitlines()
gt = set(int(l) for l in lines[3:] if l.strip())
print(f"oracle: {len(gt)}")

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
segs = find_elem_segments(p)

eid4 = set()
eid18 = set()
for sh, segid, cfg71, cnt, X, Y in segs:
    rec = sh + 24
    while is_const(u32(p, rec)) and rec < sh + cnt * 300 + 300:
        eid4.add(u32(p, rec + 4))
        e18 = u16(p, rec + 18) | (u16(p, rec + 20) << 16)
        eid18.add(e18)
        # 下一条 CONST
        j = p.find(b"\xf5\x1f\x24\x70", rec + 44, rec + 300)
        if j < 0:
            break
        rec = j
print(f"eid@+4: {len(eid4)}, in oracle: {len(eid4 & gt)}, not in oracle: {len(eid4 - gt)}")
print(f"eid@+18: {len(eid18)}, in oracle: {len(eid18 & gt)}, not in oracle: {len(eid18 - gt)}")
