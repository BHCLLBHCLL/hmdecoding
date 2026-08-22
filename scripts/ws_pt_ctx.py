import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
for pid, off in ((11573, 0x24f8), (12719, 0x3036), (12784, 0x4cf0), (12550, 0x5a6b), (12610, 0x5c0a)):
    out.append(f"=== 点 {pid} id@0x{off:x} ===")
    for o in range(off - 0x20, off + 0x50, 4):
        v = u32(o)
        tag = ""
        if v == pid:
            tag = " <== id"
        elif abs(d64(o)) < 5000 and d64(o) != 0:
            tag = f" d={round(d64(o), 4)}"
        out.append(f"  0x{o:04x}: u32={v:>9}{tag}")
open("output/ground_truth/ws_pt_ctx.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
