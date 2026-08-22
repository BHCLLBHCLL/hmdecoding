import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
out = []
v = -76.413612365723
for scale in (1, 2, 4, 8, 16, 32, 64, 128, 256, 1000, 4096, 65536):
    for fmt in ("<f", "<i", "<h"):
        try:
            val = int(round(v * scale)) if fmt != "<f" else v
            pat = struct.pack(fmt, val)
            hits = [m.start() for m in re.finditer(re.escape(pat), p)]
            if hits:
                out.append(f"y={v} scale={scale} fmt={fmt}: {len(hits)} hits {[hex(h) for h in hits[:3]]}")
        except struct.error:
            pass
open("output/ground_truth/ws_y_enc.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
