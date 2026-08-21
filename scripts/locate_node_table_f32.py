import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def f(off): return struct.unpack_from("<f", p, off)[0]
def u32(off): return struct.unpack_from("<I", p, off)[0]

NODES = {24: (5.0, -5.0, -5.0), 25: (5.0, -5.0, -5.0), 26: (5.0, -4.5, -5.0),
         100: (2.5, -5.0, -5.0), 151: (0.5, 3.0, -5.0), 442: (-3.0, -4.0, -5.0),
         443: (-3.5, -4.0, -5.0), 465: (-1.0, -3.0, -5.0)}
for nid, (x, y, z) in NODES.items():
    pat = struct.pack("<fff", x, y, z)
    offs = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"f32 node {nid}: {[hex(o) for o in offs[:6]]}")
# try the 52-byte stride from the f32 hits: node 24 (row1) at 0x7ea?
base_cands = [m.start() for m in re.finditer(re.escape(struct.pack("<fff", 5.0, -5.0, -5.0)), p)]
for base in base_cands:
    ok = True
    rows = {}
    for nid in (24, 26, 100, 151, 442, 443, 465):
        row = nid - 23
        rec = base + (row - 1) * 52
        if rec + 12 > len(p):
            ok = False; break
        got = (f(rec), f(rec+4), f(rec+8))
        exp = NODES[nid]
        if abs(got[0]-exp[0]) > 1e-4 or abs(got[1]-exp[1]) > 1e-4 or abs(got[2]-exp[2]) > 1e-4:
            ok = False; break
        rows[nid] = rec
    if ok:
        print(f"NODE TABLE FOUND (f32): base=0x{base:x}, stride 52, row=id-23")
        rec = rows[24]
        print(f"  row1: x={f(rec)} y={f(rec+4)} z={f(rec+8)}")
        print(f"  +0x0c={u32(rec+0xc)} +0x10={u32(rec+0x10)} +0x14={u32(rec+0x14)} +0x18={u32(rec+0x18)} +0x1c={u32(rec+0x1c)} +0x20={u32(rec+0x20)} +0x24={u32(rec+0x24)} +0x28={u32(rec+0x28)} +0x2c={u32(rec+0x2c)} +0x30={u32(rec+0x30)}")
