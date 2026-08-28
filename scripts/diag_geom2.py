"""dump geometry.hm Y=0 段完整记录边界."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\geometry.hm")
sh = 259682
for off in range(20, 170, 4):
    q = sh + off
    v = u32(p, q)
    print(f"  +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)})")
