import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
for v in (18, 19, 20, 21, 36, 37, 38, 39):
    hits = [m.start() for m in re.finditer(re.escape(struct.pack("<I", v)), p)]
    out.append(f"u32 {v}: {[hex(h) for h in hits[:8]]}")
# 找这些线 id 的上下文（前几个命中）
for v in (18, 36):
    hits = [m.start() for m in re.finditer(re.escape(struct.pack("<I", v)), p)]
    for h in hits[:3]:
        ctx = [u32(h + i) for i in range(-32, 48, 4)]
        out.append(f"u32 {v} @0x{h:x}: ctx={ctx}")
open("output/ground_truth/1d_lines_pos.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
