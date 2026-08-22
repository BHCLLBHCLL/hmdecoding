import gzip, struct
from collections import Counter
def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])
out = []
for name in ("v1913_geom00_empty", "v1913_geom01_p1", "v1913_geom02_p2"):
    p = load(name)
    c = Counter()
    for i in range(0, len(p) - 4, 4):
        v = struct.unpack_from("<I", p, i)[0]
        if (v >> 16) == 0x4000:
            c[v] += 1
    top = sorted(c.items(), key=lambda x: -x[1])[:10]
    out.append(f"{name} (size {len(p)}): {[(hex(v), n) for v, n in top]}")
# 也看 0x812A 类低16位家族
out.append("")
for name in ("v1913_geom00_empty", "v1913_geom01_p1", "v1913_geom02_p2"):
    p = load(name)
    c = Counter()
    for i in range(0, len(p) - 4, 4):
        v = struct.unpack_from("<I", p, i)[0]
        if (v & 0xFFFF) in (0x812A, 0x8125, 0x8126, 0x8152, 0x8127):
            c[v & 0xFFFF] += 1
    out.append(f"{name}: {dict(c)}")
open("output/ground_truth/v19_markers.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
