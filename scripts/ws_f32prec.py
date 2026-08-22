import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
pts = {11573: (1776.5, -76.413612365723, -835.0),
       12719: (1806.2435302734, -134.41250610352, -835.0),
       12784: (1776.5, -76.413612365723, -900.0)}
for pid, (x, y, z) in pts.items():
    # f32 精度转换
    yf = struct.unpack("<f", struct.pack("<f", y))[0]
    pat = struct.pack("<ddd", x, yf, z)
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    out.append(f"point {pid} (f32精度 y={yf}): {len(hits)} hits {[hex(h) for h in hits[:4]]}")
    # 也试 x/z f32 精度
    xf = struct.unpack("<f", struct.pack("<f", x))[0]
    zf = struct.unpack("<f", struct.pack("<f", z))[0]
    pat2 = struct.pack("<ddd", xf, yf, zf)
    hits2 = [m.start() for m in re.finditer(re.escape(pat2), p)]
    out.append(f"point {pid} (全f32精度): {len(hits2)} hits {[hex(h) for h in hits2[:4]]}")
open("output/ground_truth/ws_f32prec.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
