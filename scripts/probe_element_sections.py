import gzip, struct, re

def load(path):
    raw = open(path, "rb").read()
    return gzip.decompress(raw[12:])

def hits(p, pat, label):
    offs = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"{label}: {len(offs)} hits at {[hex(o) for o in offs[:10]]}")
    for o in offs[:4]:
        print(f"   @0x{o:x} pre={p[o-16:o].hex()} post={p[o+len(pat):o+len(pat)+32].hex()}")

p = load("corpus/synthetic/v1913_03_t1.hm")
hits(p, struct.pack("<I", 103), "t1 u32 103")
hits(p, struct.pack("<I", 1), "t1 u32 1 (first 10)")
# element section: after node5 ends? t1 has 4 nodes: node4 rec ends at?
pat = struct.pack("<ddd", 0.0, 0.0, 10.0)
base = [m.start() for m in re.finditer(re.escape(pat), p)]
print("t1 node4 triple candidates:", [hex(b) for b in base])

p2 = load("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
hits(p2, struct.pack("<I", 104), "1d_elements u32 104")
hits(p2, struct.pack("<I", 400), "1d_elements u32 400")
