import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def d(off): return struct.unpack_from("<d", p, off)[0]
def u32(off): return struct.unpack_from("<I", p, off)[0]

NODES = {24: (5.0, -5.0, -5.0), 25: (5.0, -5.0, -5.0), 26: (5.0, -4.5, -5.0),
         100: (2.5, -5.0, -5.0), 151: (0.5, 3.0, -5.0), 442: (-3.0, -4.0, -5.0),
         443: (-3.5, -4.0, -5.0), 465: (-1.0, -3.0, -5.0)}
for nid, (x, y, z) in NODES.items():
    pat = struct.pack("<ddd", x, y, z)
    offs = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"node {nid} ({x},{y},{z}): {[hex(o) for o in offs[:8]]}")
# hypothesis: node rows at 52-byte stride; row r = id - 23 (node 24 = row 1)
# find base: node 24/25 coords (5,-5,-5) hit — try each hit as row1 and check row 128 (= node 151) etc.
pat_a = struct.pack("<ddd", 5.0, -5.0, -5.0)
cands = [m.start() for m in re.finditer(re.escape(pat_a), p)]
for base in cands:
    ok = True
    for nid in (24, 26, 100, 151, 442, 443, 465):
        row = nid - 23
        rec = base + (row - 1) * 52
        if rec + 24 > len(p):
            ok = False; break
        got = (d(rec), d(rec+8), d(rec+16))
        exp = NODES[nid]
        if abs(got[0]-exp[0]) > 1e-9 or abs(got[1]-exp[1]) > 1e-9 or abs(got[2]-exp[2]) > 1e-9:
            ok = False; break
    if ok:
        print(f"NODE TABLE FOUND: base=0x{base:x} (row1 = node 24), 52-byte stride, row = id - 23")
        # show a record
        rec = base
        print(f"  row1 fields: +0x28={u32(rec+0x28)} +0x2c={u32(rec+0x2c)} +0x30={u32(rec+0x30)} +0x18={u32(rec+0x18)}")
