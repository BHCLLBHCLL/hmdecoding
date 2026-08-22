import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 1. 找点元数据块: [idx][0x4000812A]...
meta_blocks = []
for i in range(len(p) - 56):
    if u32(i + 4) == 0x4000812A and 1 <= u32(i) <= 100:
        block = [u32(i + j) for j in range(0, 52, 4)]
        meta_blocks.append((i, block))
out.append(f"点元数据块: {len(meta_blocks)}")
for i, b in meta_blocks:
    out.append(f"  @0x{i:x}: idx={b[0]} mark={hex(b[1])} off1={b[2]} off2={b[3]} c={b[4]} tail={b[9:13]}")
# 2. 找 0x40008126 块: [前导][mark][偏移]
geom_blocks = {}
for i in range(len(p) - 16):
    if u32(i + 4) == 0x40008126:
        geom_blocks[u32(i)] = (i, u32(i + 8))
out.append(f"0x40008126 块: {len(geom_blocks)}")
for lead, (i, off) in sorted(geom_blocks.items()):
    out.append(f"  前导={lead} @0x{i:x} 偏移=0x{off:x}")
open("output/ground_truth/point_chain.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
