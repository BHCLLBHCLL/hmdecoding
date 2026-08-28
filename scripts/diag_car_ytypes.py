"""car_section: 检查 Y=6/Y=4 段 _parse_a_type 输出 + 各段 config."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, _parse_a_type, _parse_y4_elems, _parse_b_type
from collections import Counter

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/car_section.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
rc = len(row_map)

segs = find_elem_segments(p)
# 统计每个 Y 值的产出
for Y, label in ((1, "Y=1"), (6, "Y=6"), (4, "Y=4")):
    out = {}
    for sh, segid, cfg71, cnt, X, yy in segs:
        if yy != Y:
            continue
        r = _parse_a_type(p, sh, cnt, rc, row_map)
        if r:
            out.update(r)
        if Y == 4:
            r4 = _parse_y4_elems(p, sh, cnt, rc, row_map)
            if r4:
                out.update(r4)
    cfgs = Counter(c for c, _ in out.values())
    print(f"{label}: {len(out)} elements, config hist: {dict(cfgs)}")

# 具体看 Y=6 段的记录 (seg 87)
sh, segid, cfg71, cnt, X, Y = segs[87]
r = _parse_a_type(p, sh, cnt, rc, row_map)
print("\nseg87 (Y=6) _parse_a_type:", r)
