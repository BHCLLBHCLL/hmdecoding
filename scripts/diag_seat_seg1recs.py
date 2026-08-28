"""SEAT_MODEL: seg1 首记录 @+4/@+18/nodes 与 oracle 对比."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
segs = find_elem_segments(p)
sh1 = segs[1][0]

# 首记录 CONST 在 sh+24
for idx in (0, 1, 2205, 2206, 2207, 2407):
    # 找第 idx 个 CONST
    c = None
    cnt = 0
    j = sh1
    while j < segs[2][0]:
        j = p.find(b"\xf5\x1f", j, segs[2][0])
        if j < 0:
            break
        if is_const(u32(p, j)):
            if cnt == idx:
                c = j
                break
            cnt += 1
        j += 1
    if c is None:
        print(f"record {idx}: not found")
        continue
    e4 = u16(p, c + 4)
    e18 = u16(p, c + 18)
    flag = u16(p, c + 30)
    nds = [u16(p, c + 32 + 4*i) for i in range(4)]
    print(f"record {idx} CONST@{c}: @+4={e4} @+18={e18} flag={flag} nodes={nds}")
