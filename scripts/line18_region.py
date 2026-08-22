import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
# 线 18 的 u32 位置 0x10d/0x3b2/0x7df — dump 0x380-0x450 原始字节
out.append("=== 0x380..0x450 ===")
for off in range(0x380, 0x450, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    out.append(f"0x{off:04x}  {hexs}  {ascii_}")
# 在 0x380-0x450 内找点 id 1..4 的 u32（含未对齐）
out.append("=== u32 1..4 在 0x380-0x450 ===")
for v in (1, 2, 3, 4):
    pat = struct.pack("<I", v)
    hits = [m.start() for m in re.finditer(re.escape(pat), p) if 0x380 <= m.start() < 0x450]
    out.append(f"u32 {v}: {[hex(h) for h in hits]}")
open("output/ground_truth/line18_region.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
