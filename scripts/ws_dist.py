import sys, gzip, struct, json
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
pts = {}
for line in open("output/ground_truth/ws_allpoints.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 5:
        pts[int(parts[1])] = (float(parts[2]), float(parts[3]), float(parts[4]))
pos = json.load(open("output/ground_truth/ws_pt_positions.json"))
pos = {int(k): v for k, v in pos.items()}
# 找所有点 id 块位置
blocks = {}
for i in range(0, len(p) - 8):
    v = u32(i)
    if v in pts and u32(i + 4) == 1:
        blocks[v] = i
# 距离分布: 块位置 - 三元组位置
dists = []
for pid, b in blocks.items():
    t = pos[pid]
    dists.append(b - t)
out.append(f"块-三元组距离: min={min(dists)} max={max(dists)}")
import collections
hist = collections.Counter()
for d in dists:
    if d < 0x100:
        hist["<0x100"] += 1
    elif d < 0x400:
        hist["<0x400"] += 1
    elif d < 0x1000:
        hist["<0x1000"] += 1
    else:
        hist[">=0x1000"] += 1
out.append(f"距离直方图: {dict(hist)}")
# 负距离（三元组在块后）
neg = sum(1 for d in dists if d < 0)
out.append(f"三元组在块后: {neg}")
open("output/ground_truth/ws_dist.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
