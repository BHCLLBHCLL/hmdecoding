import gzip, struct
raw = open("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm", "rb").read()
p = gzip.decompress(raw[12:])
def d64(o): return struct.unpack_from("<d", p, o)[0]
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
# 从 0x480 开始逐字节列出，标注已知值
vals = {-0.85: "n4z", -0.3: "n2z", -1.03: "n6z", -1.0: "n7z", 0.16: "n6x", 0.42: "n7x"}
i = 0x480
while i < 0x5c0:
    chunk = p[i:i+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    ann = ""
    for off in range(i, i + 16 - 8, 1):
        dv = d64(off)
        if dv in vals:
            ann += f" [{vals[dv]}@+{off-i:02x}]"
    if ann:
        out.append(f"0x{i:04x}  {hexs}  {ascii_}{ann}")
    else:
        out.append(f"0x{i:04x}  {hexs}  {ascii_}")
    i += 16
open("output/ground_truth/leg_geom_bytes.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
