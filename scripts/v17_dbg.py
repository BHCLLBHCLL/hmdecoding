"""调试 fastscan 为何漏掉 C."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

p = open("output/ground_truth/v17_payload.bin", "rb").read()
n = len(p)
ZERO4 = b"\x00\x00\x00\x00"
stride = 68
lim = 10000.0

starts = []
j = 0
while True:
    j = p.find(ZERO4, j)
    if j < 0:
        break
    base = j - 4
    if base < 0 or base + stride > n:
        j += 1
        continue
    nid = u32(p, base)
    k = u32(p, base + 8)
    if 1 <= nid <= 10_000_000 and k <= 16:
        x, y, z = d64(p, base + 12), d64(p, base + 20), d64(p, base + 28)
        if abs(x) < lim and abs(y) < lim and abs(z) < lim:
            starts.append(base)
    j += 1

print(f"total starts: {len(starts)}")
near = [s for s in starts if 29970000 < s < 29990000]
print(f"starts near C (2997xxxx-2999xxxx): {near}")
print("C targets in starts:", [b for b in (29980135, 29980203, 29980271) if b in starts])
# 检查 29980043 是否在 starts
print("29980043 in starts:", 29980043 in starts)
