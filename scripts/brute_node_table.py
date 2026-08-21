import gzip, struct

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])

NODES = {}
for line in open("output/ground_truth/node_many.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 4:
        nid = int(parts[0])
        x, y, z = (float(parts[1]), float(parts[2]), float(parts[3]))
        if abs(x) < 1e-9: x = 0.0
        if abs(y) < 1e-9: y = 0.0
        NODES[nid] = (int(round(x * 2)), int(round(y * 2)), int(round(z * 2)))  # scaled ints

def probe(base, stride, ox, oy, oz, fmt):
    """check node table with row r = id - 23 at base + (r-1)*stride; coords as fmt ints at +ox,+oy,+oz"""
    ok = 0
    fails = []
    for nid, (sx, sy, sz) in NODES.items():
        row = nid - 23
        rec = base + (row - 1) * stride
        if rec + max(ox, oy, oz) + 8 > len(p):
            return None
        try:
            vx = struct.unpack_from("<" + fmt, p, rec + ox)[0]
            vy = struct.unpack_from("<" + fmt, p, rec + oy)[0]
            vz = struct.unpack_from("<" + fmt, p, rec + oz)[0]
        except struct.error:
            return None
        if (vx, vy, vz) == (sx, sy, sz):
            ok += 1
        else:
            fails.append((nid, (vx, vy, vz), (sx, sy, sz)))
            if len(fails) > 5:
                return None
    return ok, fails

best = []
for base in range(0x0, 0x2000, 4):
    for stride in (12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 64, 72, 80):
        for ox in (0, 4, 8, 12, 16):
            for oy in (ox + 2, ox + 4):
                for oz in (oy + 2, oy + 4):
                    for fmt in ("h", "i"):
                        r = probe(base, stride, ox, oy, oz, fmt)
                        if r and r[0] >= len(NODES) - 2:
                            best.append((r[0], base, stride, ox, oy, oz, fmt, r[1]))
best.sort(reverse=True)
print("candidates:", len(best))
for b in best[:8]:
    print(f"  matches={b[0]}/{len(NODES)} base=0x{b[1]:x} stride={b[2]} ox={b[3]} oy={b[4]} oz={b[5]} fmt={b[6]} fails={b[7][:3]}")
