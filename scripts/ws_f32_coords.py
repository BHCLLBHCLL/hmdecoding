import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
out = []
# f32 1776.5 = 0x44DE2000
pat = struct.pack("<f", 1776.5)
hits = [m.start() for m in re.finditer(re.escape(pat), p)]
out.append(f"f32 1776.5 (LE {pat.hex()}): {len(hits)} hits {[hex(h) for h in hits[:6]]}")
# f32 -76.4136
pat2 = struct.pack("<f", -76.413612365723)
hits2 = [m.start() for m in re.finditer(re.escape(pat2), p)]
out.append(f"f32 -76.4136 ({pat2.hex()}): {len(hits2)} hits {[hex(h) for h in hits2[:6]]}")
# f32 -835
pat3 = struct.pack("<f", -835.0)
hits3 = [m.start() for m in re.finditer(re.escape(pat3), p)]
out.append(f"f32 -835 ({pat3.hex()}): {len(hits3)} hits {[hex(h) for h in hits3[:6]]}")
# BE 变体
pat4 = struct.pack(">f", 1776.5)
hits4 = [m.start() for m in re.finditer(re.escape(pat4), p)]
out.append(f"f32 BE 1776.5: {len(hits4)} hits {[hex(h) for h in hits4[:4]]}")
open("output/ground_truth/ws_f32_coords.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
