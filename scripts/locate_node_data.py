import gzip, struct, re

def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])

p = load("v1913_04_t2")
print("payload:", len(p))
# find known doubles
targets = {"1.0": struct.pack("<d", 1.0), "2.0": struct.pack("<d", 2.0), "3.0": struct.pack("<d", 3.0),
           "5.0": struct.pack("<d", 5.0), "10.0": struct.pack("<d", 10.0), "0.1": struct.pack("<d", 0.1),
           "2.5": struct.pack("<d", 2.5), "0.0": struct.pack("<d", 0.0)}
for label, pat in targets.items():
    offs = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"double {label}: {len(offs)} hits at {[hex(o) for o in offs[:12]]}")
# look for node-id sequences (u32 1,2,3,4,5)
for seq in ([1,2,3,4,5], [1,2,3,4], [4,3,2,1]):
    pat = b"".join(struct.pack("<I", v) for v in seq)
    offs = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"u32 seq {seq}: {len(offs)} hits at {[hex(o) for o in offs[:8]]}")
# dump region 0x0f00..0x1200 with decoding
print()
print("region 0x0f00..0x1200:")
for off in range(0x0f00, 0x1200, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    u32s = struct.unpack("<4I", chunk) if len(chunk) == 16 else ()
    print(f"{off:04x}  {hexs:<47}  {ascii_}  u32={u32s}")
