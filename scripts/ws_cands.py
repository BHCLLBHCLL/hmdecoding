import sys, gzip, struct, json
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 滑动扫描所有合理三元组: |x|,|y|,|z| < 1e5 且不全零
cands = []
i = 0
n = len(p)
while i < n - 24:
    x, y, z = d64(i), d64(i + 8), d64(i + 16)
    if abs(x) < 1e5 and abs(y) < 1e5 and abs(z) < 1e5 and (abs(x) > 1e-6 or abs(y) > 1e-6 or abs(z) > 1e-6):
        cands.append(i)
        i += 8  # 跳过重叠
    else:
        i += 1
out.append(f"候选三元组: {len(cands)}")
# 位置直方图（按 0x10000 区间）
from collections import Counter
regions = Counter(hex(i >> 16) for i in cands)
out.append(f"区域分布: {sorted(regions.items(), key=lambda x: -x[1])[:15]}")
# 与已知点位置对比
pos = json.load(open("output/ground_truth/ws_pt_positions.json"))
pos_set = set(int(v) for v in pos.values())
covered = sum(1 for v in pos_set if v in cands)
out.append(f"已知点位置在候选中: {covered}/157")
open("output/ground_truth/ws_cands.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
