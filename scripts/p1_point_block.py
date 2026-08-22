import gzip, struct, re
def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])
p0 = load("v1913_geom00_empty")
p1 = load("v1913_geom01_p1")
def u32(o): return struct.unpack_from("<I", p1, o)[0]
out = []
# 找 (1,2,3) 在 p1 中的位置 0x583 — dump 0x540-0x620
out.append("=== p1 0x540..0x620 (点1定义区) ===")
for off in range(0x540, 0x620, 4):
    v = u32(off)
    tag = ""
    if v == 0x40008126 or (v & 0xFFFF) == 0x8126 or (v & 0xFFFF) == 0x8125:
        tag = " <== 81xx 标记!"
    out.append(f"0x{off:04x}  u32={v:>10}{tag}")
# 0x40008126 类标记在 p1 中的出现
for m in re.finditer(rb"\x26\x81\x00\x40", p1):
    out.append(f"p1: 26 81 00 40 @0x{m.start():x}")
open("output/ground_truth/p1_point_block.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
