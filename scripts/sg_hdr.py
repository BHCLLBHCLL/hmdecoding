
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\solid_geom.hm")
print("len:", len(p), "db:", d64(p, 4))
# search [136] + [1][136] patterns
for i in range(0, len(p) - 24):
    if u32(p, i) == 136:
        n = u32(p, i + 4)
        if 1 <= n <= 100:
            print(f"[136]@{i} count={n} ctx={[u32(p, i+j*4) for j in range(6)]}")
# dump first 80B
print("head:", [u32(p, j*4) for j in range(16)])
