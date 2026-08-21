import gzip, struct

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def f32(off): return struct.unpack_from("<f", p, off)[0]

for off in range(0x67f0, 0x68a4, 4):
    u = u32(off)
    f = f32(off)
    annot = ""
    if 1 <= u <= 500:
        annot = f"  <-- id? {u}"
    elif abs(f) < 1000 and f != 0 and abs(f) > 1e-6:
        annot = f"  <-- coord? {f:.4f}"
    print(f"0x{off:04x}  u32={u:>10}  f32={f:>12.4f}{annot}")
