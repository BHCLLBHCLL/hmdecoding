"""dump wing_section 复合记录前 4 条 (0x1a040be4 锚定, 74B)."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
row_count = 1042

hits = []
j = 56330
while True:
    j = p.find((0x1a040be4).to_bytes(4, "little"), j, 91338)
    if j < 0:
        break
    hits.append(j); j += 1

for k in range(4):
    rec = hits[k]
    print(f"\n== rec{k} @{rec} rel={rec-56330} ==")
    for off in range(-8, 76, 4):
        q = rec + off
        if q < 0 or q + 4 > len(p):
            continue
        v = u32(p, q)
        a, b = u16(p, q), u16(p, q + 2)
        d = d64(p, q) if off % 8 == 0 else 0
        mark = ""
        if 1 <= a <= row_count:
            mark += f" <row{a}>"
        if 1 <= b <= row_count:
            mark += f" <row{b}>"
        print(f"  {off:+4d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({a},{b}) d={d:.5g}{mark}")
