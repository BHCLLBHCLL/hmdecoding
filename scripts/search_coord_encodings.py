import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def f32(off): return struct.unpack_from("<f", p, off)[0]
def d64(off): return struct.unpack_from("<d", p, off)[0]

NODES = {24: (5.0, -5.0, -5.0), 25: (5.0, -5.0, -5.0), 26: (5.0, -4.5, -5.0),
         100: (2.5, -5.0, -5.0), 151: (0.5, 3.0, -5.0), 442: (-3.0, -4.0, -5.0),
         443: (-3.5, -4.0, -5.0), 465: (-1.0, -3.0, -5.0)}
# search individual coordinate VALUES in all encodings
vals = set(v for q in NODES.values() for v in q)
print("coordinate values:", sorted(vals))
for v in sorted(vals):
    for enc, fmt in (("d64", "<d"), ("f32", "<f"), ("i32", "<i"), ("i16", "<h")):
        pat = struct.pack(fmt, v)
        offs = [m.start() for m in re.finditer(re.escape(pat), p)]
        if offs:
            print(f"  {v} as {enc}: {[hex(o) for o in offs[:8]]}")
