import gzip, struct, re

def load(name):
    raw = open(name, "rb").read()
    return gzip.decompress(raw[12:])
def u32(p, off): return struct.unpack_from("<I", p, off)[0]

def records(p):
    out = {}
    for i in range(0, len(p) - 0x30, 4):
        if u32(p, i) == 0 and u32(p, i+4) == 0x01680000:
            idx = u32(p, i + 0x24)
            if 1 <= idx <= 400:
                out[idx] = tuple(u32(p, i + 8 + j*4) for j in range(4))
    return out

p0 = load("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
r0 = records(p0)
print("baseline records:", len(r0))
print("record 40..50:")
for k in range(40, 51):
    print(f"  idx {k}: {r0.get(k)}")
