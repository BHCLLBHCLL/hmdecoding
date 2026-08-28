"""dump molding1 元素段前几条 + 节点段尾部."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, is_const

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm", "rb").read()
p = gzip.decompress(raw[12:])

sh = 666650
print("== elem seg @666650 ==")
for off in range(0, 120, 4):
    q = sh + off
    v = u32(p, q)
    mark = " <CONST>" if is_const(v) else ""
    print(f"  +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)}){mark}")

print("\n== node seg tail @182 (92B x 7279) ==")
base, stride, cnt = 182, 92, 7279
for k in range(7188, 7279):
    rec = base + k * stride
    nid = u32(p, rec + 8)
    x = d64(p, rec + 12)
    ok = 1 <= nid <= 10000000 and abs(x) < 1e9
    print(f"  k={k}: nid={nid} z4={u32(p,rec+4)} x={x:.2f} ok={ok}")
