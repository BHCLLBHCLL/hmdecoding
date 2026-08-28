"""v17 全文件扫描合法 68B/92B 节点记录起点 (mod4=3 对齐, 允许 k=0), 聚类成段."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

p = open("output/ground_truth/v17_payload.bin", "rb").read()
n = len(p)

def valid(i, stride):
    if i < 0 or i + stride > n:
        return False
    nid = u32(p, i)
    if not (1 <= nid <= 10_000_000) or u32(p, i + 4) != 0 or u32(p, i + 8) > 16:
        return False
    x, y, z = d64(p, i + 12), d64(p, i + 20), d64(p, i + 28)
    return abs(x) < 1e9 and abs(y) < 1e9 and abs(z) < 1e9

def cluster(stride, align):
    # 按 stride 和 align 扫描所有可能起点
    vset = set()
    i = align
    # 只扫描 68B 起点; 92B 的起点必然也是 68B 候选? 不. 分别扫.
    step = 4
    while i + stride <= n:
        if valid(i, stride):
            vset.add(i)
        i += step
    runs = []
    for c in sorted(vset):
        if runs and runs[-1][-1] + stride == c:
            runs[-1].append(c)
        else:
            runs.append([c])
    return [r for r in runs if len(r) >= 2]

for align in (3, 0):
    print(f"=== align mod4 = {align} ===")
    for stride in (68, 92):
        rs = cluster(stride, align)
        # 过滤: 只看大 run (>=50) 和中小 run
        big = [r for r in rs if len(r) >= 50]
        small = [r for r in rs if len(r) < 50]
        print(f"  stride={stride}: big runs={len(big)}")
        for r in big:
            print(f"    base={r[0]} cnt={len(r)} nid {u32(p,r[0])}..{u32(p,r[-1])}")
        # 只打印 nid 在 100000..9000000 且 < 20 条的小 run (排除假阳性)
        print(f"    small runs ({len(small)}):")
        for r in small[:40]:
            nids = [u32(p, x) for x in r]
            if all(1 <= v <= 10_000_000 for v in nids) and max(nids) - min(nids) < 1000:
                print(f"      base={r[0]} cnt={len(r)} nid {min(nids)}..{max(nids)} k={[u32(p,x+8) for x in r]}")
