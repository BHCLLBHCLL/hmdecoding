
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
# dump from 126+64
s = 126 + 64
for k in range(0, 220, 36):
    if s + k + 36 > len(p): break
    nid = u32(p, s + k)
    a = u32(p, s + k + 4)
    b = u32(p, s + k + 8)
    x = d64(p, s + k + 12)
    y = d64(p, s + k + 20)
    z = d64(p, s + k + 28)
    print(f"rec@{s+k-126+64:+4d}: id={nid} u4={a} u8={b} x={x:.4g} y={y:.4g} z={z:.4g}")
