"""truck: dump Y=4 与 Y=7 段结构, 判断是否也是 eid 映射问题."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
segs = find_elem_segments(p)

for sh, segid, cfg71, cnt, X, Y in segs:
    if Y not in (4, 7):
        continue
    print(f"\n===== seg {segid} Y={Y} cnt={cnt} sh={sh} =====")
    print("头 u32:", [u32(p, sh + 4*i) for i in range(8)])
    print("raw u32 (sh+24 起 20 个):", [u32(p, sh + 24 + 4*i) for i in range(20)])
    # 找 CONST
    anchor = None
    for s in range(sh + 16, sh + 400):
        if is_const(u32(p, s)):
            anchor = s; break
    print("CONST anchor:", anchor, "delta:", anchor - sh if anchor else None)
