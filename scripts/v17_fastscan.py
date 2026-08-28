"""v17 快速小簇扫描: bytes.find 零4 定位, 完整过滤, 验证只命中 C 段."""
import sys, time
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

p = open("output/ground_truth/v17_payload.bin", "rb").read()
n = len(p)
ZERO4 = b"\x00\x00\x00\x00"

def scan_small_clusters(stride, lim=10000.0):
    """返回 [(base, count, nids), ...] 2..49 条的小节点簇."""
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
        if base % 4 != 3:
            j += 1
            continue
        nid = u32(p, base)
        k = u32(p, base + 8)
        if 1 <= nid <= 10_000_000 and k <= 16:
            x, y, z = d64(p, base + 12), d64(p, base + 20), d64(p, base + 28)
            if abs(x) < lim and abs(y) < lim and abs(z) < lim:
                starts.append(base)
        j += 1
    vset = set(starts)
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
        if not any(max(abs(d64(p, x + 12)), abs(d64(p, x + 20)), abs(d64(p, x + 28))) > 0.001 for x in r):
            continue
        nids = [u32(p, x) for x in r]
        if not all(1 <= v <= 10_000_000 for v in nids):
            continue
        out.append((r[0], len(r), nids))
    return out

t0 = time.time()
for stride in (68, 92):
    cls = scan_small_clusters(stride)
    print(f"stride={stride}: {len(cls)} clusters ({(time.time()-t0):.1f}s)")
    for base, cnt, nids in cls:
        print(f"  base={base} cnt={cnt} nid={nids} k={[u32(p,base+x*stride+8) for x in range(cnt)]}")
