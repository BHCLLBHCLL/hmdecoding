
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\body_side_assembly.hm")
segs = find_elem_segments(p)
sh = None; nxt = None
for i, s in enumerate(segs):
    if s[1] == 48:
        sh = s[0]; cnt = s[3]
        nxt = segs[i+1][0] if i+1 < len(segs) else len(p)
print("seg48 @", sh, "cnt:", cnt, "next:", nxt)
# find CONST family positions in seg48
consts = []
j = sh + 24
while True:
    j = p.find(b"\xf5\x1f", j, nxt)
    if j < 0: break
    if is_const(u32(p, j)):
        consts.append(j)
    j += 1
print("const positions:", len(consts), "first:", consts[:3])
spacings = [consts[i+1]-consts[i] for i in range(min(12, len(consts)-1))]
print("spacings:", spacings)
from collections import Counter
print("spacing hist:", Counter(spacings).most_common())
