"""调试 _parse_a_type 在 molding1 344 条后断链."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, parse_nodes, find_elem_segments, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

sh, segid, cfg71, cnt, X, Y = (666650, 2, 175, 14558, 3, 1)
# 模拟 _parse_a_type, 打印前几条和断点
rec = sh + 24
print(f"first rec @{rec}: CONST={is_const(u32(p,rec))}")
# 找前 5 条 CONST 位置
consts = []
j = sh + 24
while len(consts) < 8:
    c = p.find(b"\xf5\x1f\x24\x70", j, sh + 20000)
    if c < 0:
        break
    consts.append(c)
    j = c + 1
print("first CONSTs:", consts, "spacing:", [b - a for a, b in zip(consts, consts[1:])])
# 第 344 条附近 CONST
j = sh + 24
for k in range(400):
    c = p.find(b"\xf5\x1f\x24\x70", j, j + 300)
    if c < 0:
        print(f"k={k}: no CONST from {j}")
        break
    if k >= 340:
        print(f"k={k}: CONST @{c} rel={c-sh} eid={u32(p,c+4)} eid18={u32(p,c+18)}")
    j = c + 1
