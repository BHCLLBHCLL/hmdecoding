import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
out = []
for yval in (-76.413612365723, -76.41361236, -76.413612, -76.41361, -76.4136, -76.414, -76.41, -76.4):
    pat = struct.pack("<d", yval)
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    out.append(f"y={yval}: {len(hits)} hits {[hex(h) for h in hits[:3]]}")
open("output/ground_truth/ws_y_prec.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
