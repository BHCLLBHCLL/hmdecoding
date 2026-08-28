"""dump 131694 @37995033 宽窗口 +90..+200, 找 oracle row 匹配."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

p = open("output/ground_truth/v17_payload.bin", "rb").read()
h = 37995033
orows = {116664, 116665, 36402}
lo16 = {r & 0xFFFF for r in orows}
print("oracle rows:", sorted(orows), "lo16:", sorted(lo16))
for off in range(90, 200, 4):
    q = h + off
    if q + 4 > len(p):
        break
    v = u32(p, q)
    a = u16(p, q)
    b = u16(p, q + 2)
    mark = ""
    if a in lo16 or b in lo16 or (v >> 16) in lo16:
        mark = "  <== ROW HIT"
    print(f"  +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({a},{b}){mark}")
