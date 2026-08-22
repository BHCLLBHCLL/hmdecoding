import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
pat = struct.pack("<d", 1776.5)
hits = [m.start() for m in re.finditer(re.escape(pat), p)]
out.append(f"1776.5 d64: {len(hits)} hits, 前 10: {[hex(h) for h in hits[:10]]}")
for h in hits[:3]:
    ctx = [d64(h + i) for i in range(0, 48, 8)]
    ctxu = [u32(h + i) for i in range(-8, 16, 4)]
    out.append(f"  @0x{h:x}: d64 序列={[round(v, 2) if abs(v) < 1e5 else None for v in ctx]}")
    out.append(f"    u32 ctx={ctxu}")
open("output/ground_truth/ws_x1776.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
