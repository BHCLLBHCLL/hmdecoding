import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
pat = struct.pack("<d", 1776.5)
hits = [m.start() for m in re.finditer(re.escape(pat), p)]
out.append(f"1776.5 hits: {len(hits)}")
# 打印前 6 个三元组精确值
for h in hits[:6]:
    x, y, z = d64(h), d64(h + 8), d64(h + 16)
    out.append(f"@0x{h:x}: ({x:.10f}, {y:.10f}, {z:.10f})")
# y 值分布
ys = set()
for h in hits[:50]:
    y = d64(h + 8)
    ys.add(round(y, 6))
out.append(f"前50个点的 y 值: {sorted(ys)}")
open("output/ground_truth/ws_triples.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
