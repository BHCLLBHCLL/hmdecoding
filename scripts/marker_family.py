import gzip, struct, re
from collections import Counter
def load(path):
    raw = open(path, "rb").read()
    return gzip.decompress(raw[12:])
out = []
for name, path in (("1d_elements", "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm"),
                   ("WS", "WS_3.2_3d_tetra_finish.hm"),
                   ("leg_geom", "C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm"),
                   ("spring", "C:/Program Files/Altair/2019/tutorials/hm/spring.hm")):
    p = load(path)
    c = Counter()
    for i in range(0, len(p) - 4, 4):
        v = struct.unpack_from("<I", p, i)[0]
        if (v >> 24) == 0x40 and (v & 0xFFFF) >= 0x8000 and (v & 0xFFFF) <= 0x9000:
            c[(v & 0xFFFF)] += 1
    out.append(f"{name} (nodes/elems/points/lines/surfaces):")
    out.append(f"  0x81xx/0x82xx 家族计数: {sorted(c.items(), key=lambda x: -x[1])[:12]}")
open("output/ground_truth/marker_family.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
