
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
h = 85500
for k in range(0, 120, 4):
    print(f"  {k:+3d}: {p[h+k:h+k+4].hex()} u32={u32(p,h+k):>10d} u16=({u16(p,h+k):>5d},{u16(p,h+k+2):>5d})")
