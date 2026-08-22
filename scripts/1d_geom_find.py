import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 在 0x100..0xE90 之间找线 id 1..8 的 u32 出现
for v in range(1, 9):
    hits = [m.start() for m in re.finditer(re.escape(struct.pack("<I", v)), p)]
    in_geom = [h for h in hits if 0x100 <= h < 0xE90]
    out.append(f"u32 {v}: total={len(hits)} geom区={[hex(h) for h in in_geom[:6]]}")
# dump 0x200..0x300（几何疑似区）
out.append("--- 0x200..0x300 ---")
for off in range(0x200, 0x300, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    out.append(f"0x{off:04x}  {hexs}  {ascii_}")
# dump 0x100..0x1C0
out.append("--- 0x100..0x1C0 ---")
for off in range(0x100, 0x1C0, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    out.append(f"0x{off:04x}  {hexs}  {ascii_}")
open("output/ground_truth/1d_geom_scan.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
