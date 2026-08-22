
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
# node section: base=182, stride=92
base = 182
count = 7279
bad = []
for k in range(count):
    rec = base + k * 92
    nid = u32(p, rec + 8)
    x = d64(p, rec + 20)
    if not (1 <= nid <= 10_000_000) or abs(x) > 1e9:
        bad.append((k, rec, nid, x))
print("bad records:", len(bad))
for b in bad[:10]:
    k, rec, nid, x = b
    print(f"  k={k} rec={rec}: id={nid} x={x:.3g}")
    for off in range(0, 92, 8):
        print(f"    +{off}: {p[rec+off:rec+off+8].hex()}")
