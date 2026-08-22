import gzip, struct, re
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
for pat, name in ((struct.pack("<I", 0x40008126), "0x40008126"),
                  (struct.pack("<I", 0x40026A2A), "0x40026A2A"),
                  (struct.pack("<I", 0x40008125), "0x40008125"),
                  (struct.pack("<I", 0x40088125), "0x40088125")):
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    out.append(f"{name}: {len(hits)} hits {[hex(h) for h in hits[:10]]}")
# 也检查 1d_elements 的 0x40026A2A
raw2 = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p2 = gzip.decompress(raw2[12:])
hits = [m.start() for m in re.finditer(re.escape(struct.pack("<I", 0x40026A2A)), p2)]
out.append(f"1d 0x40026A2A: {len(hits)} hits {[hex(h) for h in hits[:10]]}")
open("output/ground_truth/markers_ws.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
