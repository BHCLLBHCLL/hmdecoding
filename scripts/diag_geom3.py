"""测试 geometry Y=0: eid 连续 + 节点 u16 高, 各间距."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\geometry.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

sh = 259682
# oracle eid 1..8 nodes
oracle = {1: [20,21,61,19], 2: [19,61,62,18], 3: [21,22,63,61], 4: [61,63,64,62],
          5: [18,62,66,17], 6: [22,23,65,63], 7: [62,64,67,66], 8: [63,65,68,64]}

for stride in (40, 44, 48, 52, 56):
    ok = 0
    for k in range(8):
        rec = sh + 24 + k * stride
        # u16 高节点
        nds_hi = [(u32(p, rec + 36 + 4 * i) >> 16) for i in range(4)]
        # u32 节点 @+12
        nds_32 = [u32(p, rec + 12 + 4 * i) for i in range(4)]
        got = [row_map.get(r, r) for r in nds_hi]
        exp = oracle[k + 1]
        if sorted(got) == sorted(exp):
            ok += 1
        else:
            got2 = [row_map.get(r, r) for r in nds_32]
            if sorted(got2) == sorted(exp):
                ok += 1
    print(f"stride={stride}: matched {ok}/8")
