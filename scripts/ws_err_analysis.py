import sys, gzip, struct
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
# 所有块 + 真偏移（用 oracle 在 ±0x200 内匹配）
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
true_offsets = {}
for pid, b in blocks.items():
    x, y, z = pts[pid]
    for j in range(max(0, b - 0x200), min(b + 0x200, n - 24)):
        xs, ys, zs = d64(j), d64(j + 8), d64(j + 16)
        if abs(xs - x) < 2e-3 and abs(ys - y) < 2e-3 and abs(zs - z) < 2e-3:
            true_offsets[pid] = j - b
            break
import collections
hist = collections.Counter(true_offsets.values())
out.append(f"全部点真偏移: {hist.most_common(10)}")
# 解码错误分析
OFFSETS = (-93, -41, 15)
decoded = {}
i = 0
while i < n - 8:
    v = u32(i)
    if 10000 <= v <= 20000 and u32(i + 4) == 1 and v not in decoded:
        for off in OFFSETS:
            j = i + off
            if 0 <= j and j + 24 <= n:
                x, y, z = d64(j), d64(j + 8), d64(j + 16)
                if abs(x) < 1e5 and abs(y) < 1e5 and abs(z) < 1e5 and abs(x) > 1 and abs(y) > 1 and abs(z) > 1:
                    decoded[v] = (j, off)
                    break
        i += 8
    else:
        i += 1
bad = [pid for pid, (j, off) in decoded.items() if pid in pts and max(abs(d64(j)-pts[pid][0]), abs(d64(j+8)-pts[pid][1]), abs(d64(j+16)-pts[pid][2])) >= 2e-3]
out.append(f"错误点: {len(bad)}")
err_offsets = collections.Counter()
for pid in bad:
    err_offsets[decoded[pid][1]] += 1
out.append(f"错误点的命中偏移: {dict(err_offsets)}")
for pid in bad[:6]:
    out.append(f"  {pid}: 命中偏移={decoded[pid][1]} 真偏移={true_offsets.get(pid)}")
open("output/ground_truth/ws_err_analysis.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
