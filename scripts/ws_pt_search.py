import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
out = []
pts = {11573: (1776.5, -76.413612365723, -835.0),
       12719: (1806.2435302734, -134.41250610352, -835.0),
       12784: (1776.5, -76.413612365723, -900.0)}
for pid, (x, y, z) in pts.items():
    pat = struct.pack("<ddd", x, y, z)
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    out.append(f"point {pid} d64 triple: {[hex(h) for h in hits[:4]]}")
    # f32 triple
    try:
        patf = struct.pack("<fff", x, y, z)
        hitsf = [m.start() for m in re.finditer(re.escape(patf), p)]
        out.append(f"point {pid} f32 triple: {[hex(h) for h in hitsf[:4]]}")
    except struct.error as e:
        out.append(f"f32 err: {e}")
# 单值搜索
for pid, (x, y, z) in pts.items():
    for comp, v in (("x", x), ("y", y), ("z", z)):
        pat = struct.pack("<d", v)
        hits = [m.start() for m in re.finditer(re.escape(pat), p)]
        out.append(f"point {pid} {comp} d64: {len(hits)} hits {[hex(h) for h in hits[:4]]}")
open("output/ground_truth/ws_pt_search.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
