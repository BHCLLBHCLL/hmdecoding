"""SEAT_MODEL: seg 29 三条记录的节点位置验证 (rec+32/36/124)."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
segs = find_elem_segments(p)
sh = segs[9][0]  # seg 29
for k in range(3):
    rec = sh + 24 + k * 136
    eid = u16(p, rec + 18)
    tag = u16(p, rec + 30)
    n1 = u16(p, rec + 32)
    n2 = u16(p, rec + 36)
    n3 = u16(p, rec + 124)
    print(f"rec{k} eid={eid} tag={tag} nodes=({n1},{n2},{n3})")
