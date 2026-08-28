"""dump eid=1354 记录 + 相邻记录, 分析变体."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
MARK = b"\xe4\x0b\x04\x1a"

# 找 eid=1354
target = None
j = 56330
while True:
    j = p.find(MARK, j, 91338)
    if j < 0:
        break
    if u32(p, j + 36) == 1354:
        target = j
        break
    j += 1
print("eid=1354 @", target)
rec = target
for off in range(-4, 96, 4):
    q = rec + off
    if q < 0 or q + 4 > len(p):
        continue
    v = u32(p, q)
    a, b = u16(p, q), u16(p, q + 2)
    print(f"  {off:+4d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({a},{b})")
