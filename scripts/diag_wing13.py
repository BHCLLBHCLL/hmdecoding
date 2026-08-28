"""定位 eid=1354 的 u32 出现位置并 dump 上下文."""
import sys, gzip, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
MARK = b"\xe4\x0b\x04\x1a"

pat = struct.pack("<I", 1354)
pos = []
j = 0
while True:
    j = p.find(pat, j)
    if j < 0:
        break
    pos.append(j); j += 1
print(f"eid=1354 u32 hits: {pos}")

for h in pos:
    if 56000 <= h <= 92000:
        print(f"\n== @{h} ==")
        for off in range(-16, 96, 4):
            q = h + off
            v = u32(p, q)
            a, b = u16(p, q), u16(p, q + 2)
            mark = " <MARK>" if p[q:q+4] == MARK else ""
            print(f"  {off:+4d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({a},{b}){mark}")
