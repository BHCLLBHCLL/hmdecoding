import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
out = []
def search(v, label):
    for scale in (1, 10, 100, 1000, 10000, 65536, 2**20, 2**22, 2**24, 2**26):
        for fmt in ("<i", "<h", "<q"):
            try:
                val = int(round(v * scale))
                if fmt == "<h" and not (-32768 <= val <= 32767):
                    continue
                pat = struct.pack(fmt, val)
                hits = [m.start() for m in re.finditer(re.escape(pat), p)]
                if hits:
                    out.append(f"{label} x{scale} {fmt}: {len(hits)} {[hex(h) for h in hits[:3]]}")
            except struct.error:
                pass
search(1776.5, "x=1776.5")
search(-76.413612365723, "y=-76.4136")
open("output/ground_truth/ws_xy_int.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
