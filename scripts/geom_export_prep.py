import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 变体 A 点记录: [u32 0][d64 xyz] — 4 个点（顺序 = id 1-4）
# 点坐标已知: p1=(5,-5,0)@0x20c, p2=(5,5,0)@0x248, p3=(-5,5,0)@0x36d, p4=(-5,-5,0)@0x492
# 验证点记录并输出
pts_a = [(1, 0x20c), (2, 0x248), (3, 0x36d), (4, 0x492)]
for pid, off in pts_a:
    x, y, z = d64(off), d64(off + 8), d64(off + 16)
    out.append(f"变体A 点{pid}: ({x}, {y}, {z}) @0x{off:x}")
# 线: 显示点链验证 18=(p1,p2) 假设 — 找线 18 的实体元数据
# 之前 0x6e8 系列块（idx 26-29）与 0x40008126 块（前导 10/15/19/23）— 这些是点相关
# 线的元数据: 搜 [线id][?] 模式 — 用显示点 id 57-85（线 19/20 轮廓）
out.append("线显示点 id 57-85 覆盖: 顶边(-0.5..-5, 5) + 左边(-5, 4.5..-4.5) — 对应线 19(p2→p3)与线 20(p3→p4)")
open("output/ground_truth/geom_export_prep.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
