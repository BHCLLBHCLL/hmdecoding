import gzip, struct, re
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
def d64(off): return struct.unpack_from("<d", p, off)[0]
def u32(off): return struct.unpack_from("<I", p, off)[0]

NODES = {68519: (1547.9624571325, -126.41658730473, -879.99997278378),
         67604: (1843.9648684694, -228.95189910969, -916.0),
         70576: (1628.4970136607, -158.71059822793, -916.0),
         70468: (1603.200754327, -209.1154221864, -916.0),
         70307: (1784.4999999293, 114.79718740675, -802.82643947833)}
# find each coordinate as d64
locs = {}
for nid, (x, y, z) in NODES.items():
    for comp, v in (("x", x), ("y", y), ("z", z)):
        pat = struct.pack("<d", v)
        offs = [m.start() for m in re.finditer(re.escape(pat), p)]
        locs[(nid, comp)] = offs
        print(f"node {nid} {comp}={v}: {[hex(o) for o in offs[:5]]}")
# check for common record geometry: for each node, are x,y,z spaced consistently?
import itertools
for nid in NODES:
    xs = locs[(nid, "x")]; ys = locs[(nid, "y")]; zs = locs[(nid, "z")]
    for xo in xs[:3]:
        for yo in ys[:3]:
            for zo in zs[:3]:
                if yo - xo == 8 and zo - yo == 8:
                    print(f"  node {nid}: contiguous d64 triple at 0x{xo:x}")
                elif abs((yo - xo) - (zo - yo)) < 4 and (yo - xo) > 0:
                    print(f"  node {nid}: x@0x{xo:x} y@0x{yo:x} z@0x{zo:x} gaps {(yo-xo, zo-yo)}")
