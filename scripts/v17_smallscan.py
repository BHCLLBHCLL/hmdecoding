"""v17 小节点簇检测测试: mod4=3 网格上 68B/92B 合法记录聚类, 要求簇内至少 1 条 k>=1, 2..49 条."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section_struct

p = open("output/ground_truth/v17_payload.bin", "rb").read()
n = len(p)

def valid_rec(i, stride, lim=10000.0):
    if i < 0 or i + stride > n:
        return False
    nid = u32(p, i)
    if not (1 <= nid <= 10_000_000) or u32(p, i + 4) != 0 or u32(p, i + 8) > 16:
        return False
    x, y, z = d64(p, i + 12), d64(p, i + 20), d64(p, i + 28)
    return abs(x) < lim and abs(y) < lim and abs(z) < lim

# 现有大段范围 (用于排除)
big = sorted(find_node_section_struct(p, multi=True), key=lambda s: s[2])
big_ranges = [(s[2], s[2] + s[1] * s[3]) for s in big]
print("big segs:", [(s[2], s[1], s[3]) for s in big])

def find_small_clusters(stride, align):
    vset = set()
    i = align
    while i + stride <= n:
        if valid_rec(i, stride):
            vset.add(i)
        i += 4
    runs = []
    for c in sorted(vset):
        if runs and runs[-1][-1] + stride == c:
            runs[-1].append(c)
        else:
            runs.append([c])
    out = []
    for r in runs:
        if not (2 <= len(r) <= 49):
            continue
        if not any(1 <= u32(p, x + 8) <= 16 for x in r):
            continue
        # 不做范围排除, 全部列出 (仅 68B, 含 k>=1 要求)
        nids = [u32(p, x) for x in r]
        if not all(1 <= v <= 10_000_000 for v in nids):
            continue
        out.append((r[0], len(r), nids))
    return out

for align in (3,):
    for stride in (68, 92):
        cls = find_small_clusters(stride, align)
        print(f"\nalign={align} stride={stride}: {len(cls)} small clusters")
        for base, cnt, nids in cls:
            inbig = any(a <= base < b for a, b in big_ranges)
            print(f"  base={base} cnt={cnt} inbig={inbig} nid {nids[:8]}... k={[u32(p,base+x*stride+8) for x in range(min(cnt,6))]} "
                  f"xyz0=({d64(p,base+12):.1f},{d64(p,base+20):.1f},{d64(p,base+28):.1f})")
