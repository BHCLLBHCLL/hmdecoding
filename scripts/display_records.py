import gzip, struct
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def d64(o): return struct.unpack_from("<d", p, o)[0]
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
# 滑动: 每个 4 字节位置检查 d64 是否合理坐标
i = 0x1528
while i < 0x1700:
    dv = d64(i)
    uv = u32(i)
    tag = ""
    if abs(dv) < 20 and abs(dv) > 1e-9:
        tag = f" d64={dv:.4f}"
    elif 1 <= uv <= 100:
        tag = f" u32={uv}"
    elif dv == 0.0:
        tag = " d64=0"
    if tag:
        out.append(f"0x{i:04x}:{tag}")
    i += 4
open("output/ground_truth/display_records.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
