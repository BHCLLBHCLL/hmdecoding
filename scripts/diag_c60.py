"""dump standard_section_complete seg@2082 (config 60, B 型)."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\standard_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])

sh = 2082
print("== seg @2082 ==")
for off in range(0, 240, 4):
    q = sh + off
    if q + 4 > len(p):
        break
    v = u32(p, q)
    print(f"  +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)})")
