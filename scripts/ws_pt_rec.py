import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 1. 点 11529: 三元组@0xccdf → 块@0xcd3c — 完整 1 字节 dump
out.append("=== 11529: 0xccd8..0xcd50 (1字节) ===")
for off in range(0xccd8, 0xcd50, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    out.append(f"0x{off:04x}  {hexs}  {ascii_}")
# 2. 在 11573 块内滑动找坐标
out.append("=== 11573 块 @0x24f8 内滑动找 (1776.5, -76.4, -835) ===")
for off in range(0x24f8, min(0x24f8 + 0x200, len(p) - 24)):
    x, y, z = d64(off), d64(off + 8), d64(off + 16)
    if abs(x - 1776.5) < 1e-3 and abs(z + 835) < 1e-3 and abs(y + 76.41) < 1e-2:
        out.append(f"  FOUND @0x{off:x}: ({x:.6f}, {y:.6f}, {z:.6f})")
out.append("  (无匹配则未找到)")
open("output/ground_truth/ws_pt_rec.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
