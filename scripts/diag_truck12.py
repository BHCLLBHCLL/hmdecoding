"""定位 truck 缺失 eid (212715+) 的字节位置."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")

for eid in (212715, 212716, 219670, 220000, 228633, 100):
    pat = eid.to_bytes(4, "little")
    pos = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        pos.append(j); j += 1
    print(f"eid {eid}: hits {pos[:6]}")

# 这些位置属于哪个段
segs = find_elem_segments(p)
def seg_of(pos):
    cur = None
    for s in segs:
        if s[0] <= pos:
            cur = s
        else:
            break
    return cur

# 缺失 eid 区间的段分布
ranges = [(212715, 219669), (219677, 220409), (220411, 228633)]
for eid in (212715, 220000, 228633):
    pat = eid.to_bytes(4, "little")
    j = p.find(pat)
    if j >= 0:
        s = seg_of(j)
        print(f"eid {eid} @{j} in seg {s[1] if s else None} Y={s[5] if s else None}")
