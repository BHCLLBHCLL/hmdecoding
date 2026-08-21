import gzip, struct
def load(name):
    raw = open(name, "rb").read()
    return gzip.decompress(raw[12:])
def u32(p, off): return struct.unpack_from("<I", p, off)[0]
p0 = load("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
p1 = load("corpus/synthetic/1d_del_elem5.hm")
print("sizes:", len(p0), len(p1))
def recs(p):
    out = {}
    for i in range(0, len(p) - 0x30, 4):
        if u32(p, i) == 0 and u32(p, i+4) == 0x01680000:
            idx = u32(p, i + 0x24)
            if 1 <= idx <= 401:
                out[idx] = tuple(u32(p, i + 8 + j*4) for j in range(4))
    return out
r0, r1 = recs(p0), recs(p1)
print("records:", len(r0), "->", len(r1))
gone = [k for k in r0 if k not in r1]
new = [k for k in r1 if k not in r0]
print("gone:", gone, "new:", new)
for k in sorted(set(r0) & set(r1))[:5]:
    pass
# show which record quads vanished entirely
q0 = set(r0.values()); q1 = set(r1.values())
print("quads lost:", [q for q in q0 - q1])
print("quads gained:", [q for q in q1 - q0])
