import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 点 11529: 三元组@0xccdf 块@0xcd3c — dump 0xccd0-0xcd50
for off in range(0xccd0, 0xcd50, 4):
    v = u32(off)
    tag = ""
    if v == 11529:
        tag = " <== id"
    elif abs(d64(off)) < 5000 and d64(off) != 0:
        tag = f" d={round(d64(off), 4)}"
    out.append(f"0x{off:04x}: u32={v:>9}{tag}")
open("output/ground_truth/ws_pt11529.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
