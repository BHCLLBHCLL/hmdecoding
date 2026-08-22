import gzip, struct
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
for m in (0x1ad, 0x30a, 0x42f, 0x554):
    out.append(f"=== 0x{m:x} 上下文 (0x40008126) ===")
    for off in range(m - 0x20, m + 0x50, 4):
        v = u32(off)
        tag = ""
        if v == 0x40008126:
            tag = " <== MARKER"
        elif v < 30:
            tag = " <id?>"
        out.append(f"0x{off:04x}  u32={v:>10}{tag}")
open("output/ground_truth/marker_ctx.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
