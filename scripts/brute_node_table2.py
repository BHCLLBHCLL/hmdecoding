import gzip, struct

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])

NODES = {}
for line in open("output/ground_truth/node_many.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 4:
        nid = int(parts[0])
        x, y, z = (float(parts[1]), float(parts[2]), float(parts[3]))
        NODES[nid] = (x, y, z)

def getv(off, fmt):
    try:
        return struct.unpack_from("<" + fmt, p, off)[0]
    except struct.error:
        return None

anchors = [24, 26, 100, 151, 442, 465]
cands = []
for base in range(0x1000, 0x68c0, 4):
    for stride in (12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 72, 80, 96):
        last_rec = base + 441 * stride
        if last_rec + 40 > 0x68c0:
            continue
        for ox in range(0, 24, 4):
            for oy in (ox + 2, ox + 4, ox + 8):
                for oz in (oy + 2, oy + 4, oy + 8):
                    for fmt in ("h", "i", "f", "d"):
                        sz = struct.calcsize(fmt)
                        ok = True
                        for nid in anchors:
                            row = nid - 23
                            rec = base + (row - 1) * stride
                            vals = (getv(rec + ox, fmt), getv(rec + oy, fmt), getv(rec + oz, fmt))
                            exp = NODES[nid]
                            if any(v is None for v in vals):
                                ok = False; break
                            if fmt in ("f", "d"):
                                if abs(vals[0] - exp[0]) > 1e-4 or abs(vals[1] - exp[1]) > 1e-4 or abs(vals[2] - exp[2]) > 1e-4:
                                    ok = False; break
                            else:
                                if (vals[0], vals[1], vals[2]) != (round(exp[0]*2), round(exp[1]*2), round(exp[2]*2)):
                                    ok = False; break
                        if ok:
                            cands.append((base, stride, ox, oy, oz, fmt))
print("candidates:", len(cands))
for c in cands[:10]:
    print(" ", hex(c[0]), c)
