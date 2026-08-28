"""dump shell_section.hm [136]头@229 后的记录."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

p = open(r"C:\Program Files\Altair\2019\tutorials\hm\shell_section.hm", "rb").read()
import gzip
raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\shell_section.hm", "rb").read()
p = gzip.decompress(raw[12:])
print(f"payload {len(p)}")

h = 229
print(f"[136] head @{h}: count={u32(p, h+4)}")
for off in range(0, 200, 4):
    q = h + off
    if q + 4 > len(p):
        break
    v = u32(p, q)
    d = d64(p, q) if q + 8 <= len(p) else 0
    print(f"  +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} d={d:.6g}")
