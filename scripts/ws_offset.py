import sys, gzip, struct, json
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
pts = {}
for line in open("output/ground_truth/ws_allpoints.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 5:
        pts[int(parts[1])] = (float(parts[2]), float(parts[3]), float(parts[4]))
# 对每个块: 在 ±0x200 内找与 oracle 容差匹配的三元组 → 偏移分布
blocks = {}
i = 0
n = len(p)
while i < n - 8:
    v = u32(i)
    if v in pts and u32(i + 4) == 1:
        blocks[v] = i
        i += 8
    else:
        i += 1
offsets = []
found = 0
for pid, b in blocks.items():
    x, y, z = pts[pid]
    best = None
    for j in range(max(0, b - 0x200), min(b + 0x200, n - 24)):
        xs, ys, zs = d64(j), d64(j + 8), d64(j + 16)
        if abs(xs - x) < 2e-3 and abs(ys - y) < 2e-3 and abs(zs - z) < 2e-3:
            best = j
            break
    if best is not None:
        offsets.append(best - b)
        found += 1
out.append(f"±0x200 内匹配: {found}/{len(blocks)}")
import collections
hist = collections.Counter()
for d in offsets:
    if -0x80 <= d <= 0x80:
        hist[d] += 1
    elif d < 0:
        hist["<-0x80"] += 1
    else:
        hist[">0x80"] += 1
out.append(f"偏移直方图(字节): {sorted(hist.items(), key=lambda x: -x[1] if isinstance(x[0], int) else 0)[:12]}")
out.append(f"正偏移(坐标在块后): {sum(1 for d in offsets if d > 0)} 负偏移: {sum(1 for d in offsets if d < 0)}")
open("output/ground_truth/ws_offset.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
