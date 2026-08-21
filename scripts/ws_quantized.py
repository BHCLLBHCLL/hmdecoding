import gzip, struct, re
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
NODES = {68519: (1547.9624571325, -126.41658730473, -879.99997278378),
         67604: (1843.9648684694, -228.95189910969, -916.0),
         70576: (1628.4970136607, -158.71059822793, -916.0),
         70468: (1603.200754327, -209.1154221864, -916.0),
         70307: (1784.4999999293, 114.79718740675, -802.82643947833)}
st = struct
for nid, (x, y, z) in NODES.items():
    found = []
    for comp, v in (("x", x), ("y", y), ("z", z)):
        pats = {
            "f32": st.pack("<f", v),
            "i32x100": st.pack("<i", int(round(v * 100))),
            "i32x1000": st.pack("<i", int(round(v * 1000))),
            "i32x4096": st.pack("<i", int(round(v * 4096))),
        }
        for enc, pat in pats.items():
            offs = [m.start() for m in re.finditer(re.escape(pat), p)]
            if offs:
                found.append((comp, enc, [hex(o) for o in offs[:3]]))
    print(f"node {nid}: {found if found else 'NOTHING'}")
