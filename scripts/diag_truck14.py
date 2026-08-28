"""dump truck seg 2000001 (Y=1) 记录."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
sh = 11376800
print(f"== seg @{sh} ==")
for off in range(0, 140, 4):
    q = sh + off
    v = u32(p, q)
    mark = " <CONST>" if is_const(v) else ""
    print(f"  +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)}){mark}")
