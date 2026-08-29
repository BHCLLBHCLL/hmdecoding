
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
MARK = b"\xe4\x0b\x04\x1a"
segs = []
import re
# seg8 span
sh = 56330; nxt = 91338
hits = []
j = sh + 24
while j < nxt:
    j = p.find(MARK, j, nxt)
    if j < 0: break
    hits.append(j)
    j += 1
h = hits[393]
print(f"=== bad record @{h} (k=393) === mid={h-sh}")
for k in range(0, 104, 4):
    print(f"  +{k:3d}: {p[h+k:h+k+4].hex()} u32={u32(p,h+k):>10d} u16=({u16(p,h+k):>5d},{u16(p,h+k+2):>5d})")
# good record k=394 for comparison
h2 = hits[394]
print(f"=== good record @{h2} (k=394) ===")
for k in range(0, 84, 4):
    print(f"  +{k:3d}: {p[h2+k:h2+k+4].hex()} u32={u32(p,h2+k):>10d}")
