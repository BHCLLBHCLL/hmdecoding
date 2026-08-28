"""dump 57060..57140 找 eid=1354 记录头."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])

for off in range(57060, 57140, 4):
    q = off
    v = u32(p, q)
    a, b = u16(p, q), u16(p, q + 2)
    mark = ""
    if v == 0x1a040be4:
        mark = " <0x1a040be4>"
    if v == 0x0a040be6:
        mark = " <0x0a040be6>"
    if v == 0x12040084:
        mark = " <0x12040084>"
    if 0 < v < 3000:
        mark += f" <eid?{v}>"
    print(f"{q}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({a},{b}){mark}")
