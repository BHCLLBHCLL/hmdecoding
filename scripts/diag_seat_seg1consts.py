"""SEAT_MODEL: 统计 seg1 区域 CONST 锚点, 定位 5544/5545 记录."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
segs = find_elem_segments(p)
sh1 = segs[1][0]  # seg 1
sh2 = segs[2][0]  # seg 2
print("seg1 sh:", sh1, "seg2 sh:", sh2)

# 找 seg1 区域内所有 CONST 锚点
consts = []
j = sh1
while j < sh2:
    j = p.find(b"\xf5\x1f", j, sh2)
    if j < 0:
        break
    if is_const(u32(p, j)):
        consts.append(j)
    j += 1
print("num CONST in seg1 region:", len(consts))
print("first 3:", consts[:3], "last 3:", consts[-3:])

# 看最后几个 CONST 对应的 eid (@+18) 和 flag (@+30)
for c in consts[-6:]:
    eid = u16(p, c + 18) | (u16(p, c + 20) << 16)
    e4 = u16(p, c + 4)
    flag = u16(p, c + 30)
    print(f"  CONST @ {c}: @+4={e4} @+18={eid} flag@{c+30}={flag}")
