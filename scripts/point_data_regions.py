import gzip, struct
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
def f32(o): return struct.unpack_from("<f", p, o)[0]
out = []
for base in (0x1500, 0x1700, 0x1900, 0x1B00):
    out.append(f"=== 0x{base:x} (点几何数据区) ===")
    for off in range(base, base + 0x200, 16):
        chunk = p[off:off+16]
        hexs = " ".join(f"{b:02x}" for b in chunk)
        ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        out.append(f"0x{off:04x}  {hexs}  {ascii_}")
open("output/ground_truth/point_data_regions.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
