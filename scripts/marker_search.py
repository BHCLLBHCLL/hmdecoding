import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
# 0x40008126 的出现
pat = struct.pack("<I", 0x40008126)
hits = [m.start() for m in re.finditer(re.escape(pat), p)]
out.append(f"0x40008126 hits: {[hex(h) for h in hits[:10]]}")
# 类似模式 0x40008xxx
for m in re.finditer(rb"\x26\x81\x00\x40", p):
    out.append(f"26 81 00 40 @0x{m.start():x}")
# dump 0x428..0x4c0
out.append("=== 0x428..0x4c0 ===")
for off in range(0x428, 0x4c0, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    out.append(f"0x{off:04x}  {hexs}  {ascii_}")
open("output/ground_truth/marker_search.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
