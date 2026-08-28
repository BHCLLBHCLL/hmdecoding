"""dump wing_section_complete seg@56330 (X=3 A 型 config 104)."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, is_const

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])

for sh in (56330, 91338):
    print(f"\n== seg @{sh} ==")
    for off in range(0, 160, 4):
        q = sh + off
        if q + 4 > len(p):
            break
        v = u32(p, q)
        mark = " <CONST>" if is_const(v) else ""
        print(f"  +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)}){mark}")
