"""SEAT_MODEL: 找 @+4 != eid@+18 的记录, 看差异."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
segs = find_elem_segments(p)

diffs = []
shown = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    rec = sh + 24
    for k in range(min(cnt, 200)):
        if not is_const(u32(p, rec)):
            break
        e18 = u16(p, rec + 18) | (u16(p, rec + 20) << 16)
        e4 = u32(p, rec + 4)
        if u32(p, rec + 8) in (0x02BD0002, 0x02AE0002) and u16(p, rec + 12) == 2596 and e4 != e18:
            diffs.append((e4, e18, segid))
            if shown < 8:
                print(f"seg {segid}: @+4={e4} eid@+18={e18} diff={e4-e18} rec@{rec}")
                shown += 1
        j = p.find(b"\xf5\x1f\x24\x70", rec + 44, rec + 300)
        if j < 0:
            break
        rec = j
print(f"total diffs seen: {len(diffs)}")
# 差异统计
if diffs:
    import collections
    d = collections.Counter(b - a for a, b in diffs)
    print("diff dist:", d.most_common(10))
