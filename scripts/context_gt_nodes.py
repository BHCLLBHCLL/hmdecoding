import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]

# context of node 146 and 151 (elem 1 GT nodes)
for val in (146, 151, 133, 134):
    pat = struct.pack("<I", val)
    offs = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"u32 {val}: {len(offs)} hits: {[hex(o) for o in offs[:12]]}")
# dump contexts around the first few hits of 146
offs146 = [m.start() for m in re.finditer(re.escape(struct.pack("<I", 146)), p)]
for o in offs146[:6]:
    s = max(0, o - 24)
    vals = [u32(s + i*4) for i in range(13)]
    print(f"@0x{o:x}: {vals}")
