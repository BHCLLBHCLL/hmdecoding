import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm")
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 节点坐标（oracle 已知）
NODES = {2: (0.0, 0.0, -0.3), 4: (0.0, 0.0, -0.85), 6: (0.16, 0.0, -1.03), 7: (0.42, 0.0, -1.0)}
# 在几何区（0x484+）搜每个节点的完整三元组（容差 1e-3）
for nid, (x, y, z) in NODES.items():
    hits = []
    for i in range(0x484, len(p) - 24):
        x2, y2, z2 = d64(i), d64(i + 8), d64(i + 16)
        if abs(x2 - x) < 1e-3 and abs(y2 - y) < 1e-3 and abs(z2 - z) < 1e-3:
            hits.append(i)
    out.append(f"节点 {nid} ({x},{y},{z}): 几何区三元组 {[hex(h) for h in hits[:5]]}")
# 线 id 1,2,4 在几何区的位置（u32，1字节滑动）
def u32(o): return struct.unpack_from("<I", p, o)[0]
for lid in (1, 2, 4):
    hits = [i for i in range(0x484, len(p) - 4) if u32(i) == lid]
    out.append(f"线 {lid}: 几何区 u32 位置 {[hex(h) for h in hits[:8]]}")
open("output/ground_truth/leg_lines_final.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
