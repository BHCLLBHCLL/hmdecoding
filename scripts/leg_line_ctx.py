import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
# 线 id 位置附近 ±0x30 内的 u32（找节点 id 2/4/6/7 引用）
for lid, pos in ((1, 0x4de), (2, 0x56b), (4, 0x584), (1, 0x79f), (2, 0x82c), (4, 0x9cb)):
    out.append(f"线 {lid} @0x{pos:x}: 附近 u32 = {[u32(pos + j) for j in range(-0x20, 0x30, 4)]}")
open("output/ground_truth/leg_line_ctx.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
