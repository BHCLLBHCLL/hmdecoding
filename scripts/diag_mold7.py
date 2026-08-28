"""复现 _scan_extra_node_segs 的收集逻辑, 检查 661726-666700 的 starts."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
n = len(p)
ZERO4 = b"\x00\x00\x00\x00"
lim = 10000.0

starts = {52: [], 56: [], 68: [], 92: []}
j = 0
while True:
    j = p.find(ZERO4, j)
    if j < 0:
        break
    base = j - 4
    if base < 0:
        j += 1
        continue
    nid = u32(p, base)
    k = u32(p, base + 8)
    if not (1 <= nid <= 10_000_000 and k <= 16):
        j += 1
        continue
    for stride in (52, 56, 68, 92):
        if base + stride > n:
            continue
        x, y, z = d64(p, base + 12), d64(p, base + 20), d64(p, base + 28)
        if abs(x) < lim and abs(y) < lim and abs(z) < lim:
            starts[stride].append(base)
    j += 1

for stride in (52, 56):
    near = [b for b in starts[stride] if 660000 < b < 667000]
    print(f"starts[{stride}] near 660-667k: {near[:20]}")
    # run 分析
    vset = set(near)
    runs = []
    for c in sorted(vset):
        if runs and runs[-1][-1] + stride == c:
            runs[-1].append(c)
        else:
            runs.append([c])
    big = [r for r in runs if len(r) >= 3]
    print(f"  runs >=3: {[(r[0], len(r)) for r in big]}")
