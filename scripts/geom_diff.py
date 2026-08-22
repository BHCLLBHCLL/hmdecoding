import gzip, struct, re
def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])
p0 = load("v1913_geom00_empty")
p1 = load("v1913_geom01_p1")
p2 = load("v1913_geom02_p2")
print("sizes:", len(p0), len(p1), len(p2))
# 点 1 = (1,2,3) 的 d64 三元组在 p1 中的位置
pat = struct.pack("<ddd", 1.0, 2.0, 3.0)
hits = [m.start() for m in re.finditer(re.escape(pat), p1)]
print("(1,2,3) hits:", [hex(h) for h in hits[:8]])
for h in hits[:3]:
    print(f"  @0x{h:x} pre={p1[h-24:h].hex()}")
# 点 2 = (4,5,6) 在 p2 中
pat2 = struct.pack("<ddd", 4.0, 5.0, 6.0)
hits2 = [m.start() for m in re.finditer(re.escape(pat2), p2)]
print("(4,5,6) hits:", [hex(h) for h in hits2[:8]])
# 两个点同时存在时 (1,2,3) 的位置
hits12 = [m.start() for m in re.finditer(re.escape(pat), p2)]
print("(1,2,3) in p2:", [hex(h) for h in hits12[:8]])
# 差分区域
def diff_regions(a, b):
    n = min(len(a), len(b))
    regs = []; start = None
    for i in range(0, n, 4):
        if a[i:i+4] != b[i:i+4]:
            if start is None: start = i
        else:
            if start is not None: regs.append((start, i)); start = None
    if start is not None: regs.append((start, n))
    return regs
for name, x, y in (("p0->p1", p0, p1), ("p1->p2", p1, p2)):
    regs = diff_regions(x, y)
    print(f"{name}: {len(regs)} regions, first 10: {[(hex(a), hex(b)) for a, b in regs[:10]]}")
