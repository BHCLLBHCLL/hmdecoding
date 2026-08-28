"""扫描 geometry Y=0 段内所有 CONST 标记及结构."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\geometry.hm")
ns = find_node_section(p)
segs = find_elem_segments(p)
sh = segs[0][0]
cnt = segs[0][3]
print("seg:", segs[0], "cnt", cnt)

# 找段内所有 CONST
consts = []
end = min(len(p), sh + 200000)
j = sh
while True:
    j = p.find(b"\xf5\x1f", j, end)
    if j < 0:
        break
    if is_const(u32(p, j)):
        consts.append(j)
    j += 1
print("CONST count in region:", len(consts))
for c in consts[:30]:
    print(f"  CONST @ {c} (sh+{c-sh})")

# dump 前几个 CONST 附近
for c in consts[:4]:
    print(f"\n== CONST @ {c} (sh+{c-sh}) ==")
    for off in range(0, 96, 2):
        q = c + off
        print(f"  +{off:3d}: {p[q:q+2].hex(' ')} u16={u16(p,q):<6d}")
