
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
# find seg 2000290
sh = None
i = 0
while i < len(p) - 24:
    if u32(p, i) == 997 and u32(p, i+4) == 2000290:
        sh = i; break
    i += 1
print("seg 2000290 @", sh, "header:", [u32(p, sh+j*4) for j in range(6)] if sh else None)
if sh:
    s = sh + 24
    for k in range(0, 64, 4):
        print(f"  +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>9d} u16=({u16(p,s+k):>5d},{u16(p,s+k+2):>5d})")
