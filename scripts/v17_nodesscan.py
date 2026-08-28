"""v17 全文件扫描合法 68B/92B 节点记录起点 (允许 k=0), 聚类成段."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

p = open("output/ground_truth/v17_payload.bin", "rb").read()
n = len(p)
print(f"payload {n} bytes")

def valid68(i):
    if i < 0 or i + 68 > n:
        return False
    nid = u32(p, i)
    if not (1 <= nid <= 10_000_000) or u32(p, i + 4) != 0 or u32(p, i + 8) > 16:
        return False
    try:
        x, y, z = d64(p, i + 12), d64(p, i + 20), d64(p, i + 28)
    except Exception:
        return False
    return abs(x) < 1e9 and abs(y) < 1e9 and abs(z) < 1e9

def valid92(i):
    if i < 0 or i + 92 > n:
        return False
    nid = u32(p, i)
    if not (1 <= nid <= 10_000_000) or u32(p, i + 4) != 0 or u32(p, i + 8) > 16:
        return False
    try:
        x, y, z = d64(p, i + 12), d64(p, i + 20), d64(p, i + 28)
    except Exception:
        return False
    return abs(x) < 1e9 and abs(y) < 1e9 and abs(z) < 1e9

# 用 bytes.find 快速定位候选: [nid][0][k] 中 @+4 为 0
# 搜索所有 4 字节 0 的位置, 检查其前 4 字节
ZERO4 = b"\x00\x00\x00\x00"
cands = []
start = 0
while True:
    j = p.find(ZERO4, start)
    if j < 0:
        break
    i = j - 4
    if i >= 0 and u32(p, i) >= 1 and u32(p, i) <= 10_000_000:
        cands.append(i)
    start = j + 1
print(f"cand positions: {len(cands)}")

# 对每个候选检查 68B/92B 有效性, 聚类
def cluster(cands, stride, validfn):
    vset = set(c for c in cands if validfn(c))
    # 用集合找最长连续 run (按 stride 递增)
    runs = []
    for c in sorted(vset):
        if runs and runs[-1][-1] + stride == c:
            runs[-1].append(c)
        else:
            runs.append([c])
    return [r for r in runs if len(r) >= 2]

r68 = cluster(cands, 68, valid68)
r92 = cluster(cands, 92, valid92)
print("\n68B runs (>=2):")
for r in sorted(r68, key=lambda r: r[0]):
    print(f"  base={r[0]} cnt={len(r)} nid {u32(p,r[0])}..{u32(p,r[-1])} k={[u32(p, x+8) for x in r[:4]]}")
print("\n92B runs (>=2):")
for r in sorted(r92, key=lambda r: r[0]):
    print(f"  base={r[0]} cnt={len(r)} nid {u32(p,r[0])}..{u32(p,r[-1])}")
