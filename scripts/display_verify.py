import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 1. 显示网格记录: 从 0x1500 起 52 字节步进
out.append("=== 显示网格记录 (0x1530 起 52B 步进) ===")
for base in range(0x1530, 0x1B00, 52):
    x, y, z = d64(base), d64(base + 8), d64(base + 16)
    d1, d2 = d64(base + 24), d64(base + 32)
    rid = u32(base + 40)
    out.append(f"@0x{base:04x}: ({x:.2f}, {y:.2f}, {z:.2f}) [{d1},{d2}] id={rid} next={u32(base+44)},{u32(base+48)}")
# 2. 0x40008126 数据块 → 偏移 → 显示区
out.append("=== 0x40008126 块 → 偏移 ===")
for base in (0x554,):
    for off in range(base, base + 32, 4):
        out.append(f"  0x{off:04x}: u32={u32(off)}")
open("output/ground_truth/display_verify.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
