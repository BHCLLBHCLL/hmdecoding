import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def u16(o): return struct.unpack_from("<H", p, o)[0]
def f32(o): return struct.unpack_from("<f", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
out.append("=== 点 11573 块 @0x24f8, 0x24d0-0x2560 ===")
for off in range(0x24d0, 0x2560, 8):
    u1, u2 = u32(off), u32(off + 4)
    dv = d64(off)
    f1, f2 = f32(off), f32(off + 4)
    h1, h2 = u16(off), u16(off + 2)
    h3, h4 = u16(off + 4), u16(off + 6)
    tag = ""
    if abs(dv) < 5000 and dv != 0:
        tag += f" D={round(dv,4)}"
    if abs(f1) < 5000 and f1 != 0:
        tag += f" f1={round(f1,4)}"
    if abs(f2) < 5000 and f2 != 0:
        tag += f" f2={round(f2,4)}"
    out.append(f"0x{off:04x}: u32=({u1},{u2}) u16=({h1},{h2},{h3},{h4}){tag}")
open("output/ground_truth/ws_pt11573_full.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
