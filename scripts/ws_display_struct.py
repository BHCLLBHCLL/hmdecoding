import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 搜索 WS 中的 52B 显示记录候选: [d64 x][d64 y][d64 z][0][0][u32 id]
# 用已知坐标锚定: 节点 67604 = (1843.96, -228.95, -916)
cands = []
for i in range(0, len(p) - 52, 4):
    x, y, z = d64(i), d64(i + 8), d64(i + 16)
    if abs(x - 1843.96) < 0.01 and abs(y + 228.95) < 0.01 and abs(z + 916) < 0.01:
        cands.append((i, u32(i + 40)))
out.append(f"节点67604坐标的52B记录候选: {[(hex(c), r) for c, r in cands[:8]]}")
# 0x40008126 上下文（WS）: 前几个
marks = [i for i in range(len(p) - 8) if u32(i) == 0x40008126]
out.append(f"WS 0x40008126: {len(marks)} 个")
for m in marks[:3]:
    ctx = [u32(m + j) for j in range(-8, 24, 4)]
    out.append(f"  @0x{m:x} ctx={ctx}")
open("output/ground_truth/ws_display_struct.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
