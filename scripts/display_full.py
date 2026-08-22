import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 逐字节找 MARK_GEOM
marks = []
for i in range(len(p) - 8):
    if u32(i) == 0x40008126:
        marks.append(i)
out.append(f"MARK_GEOM 逐字节: {[hex(m) for m in marks]}")
for m in marks:
    off = u32(m + 4)
    out.append(f"  @0x{m:x}: offset={off} (0x{off:x})")
# 解码偏移指向的区域（记录从区块内找 52B 记录）
points = {}
for m in marks:
    off = u32(m + 4)
    # 在 off 起 0x200 内找记录流: 检查 52 步进的记录
    for start in range(off, off + 0x100, 4):
        x = d64(start)
        if abs(x) < 1000 and x != 0:
            pts = []
            base = start
            while base + 52 <= len(p):
                x2, y2, z2 = d64(base), d64(base + 8), d64(base + 16)
                rid = u32(base + 40)
                if not (abs(x2) < 1000 and abs(z2) < 1000):
                    break
                pts.append((rid, round(x2, 3), round(y2, 3), round(z2, 3)))
                base += 52
            if len(pts) >= 3:
                out.append(f"  mark@0x{m:x} offset=0x{off:x} -> 记录流 @0x{start:x}: {len(pts)} 条, 首={pts[:3]}, 尾={pts[-2:]}")
                break
open("output/ground_truth/display_full.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
