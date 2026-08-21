import gzip, struct, re
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d64(off): return struct.unpack_from("<d", p, off)[0]
# node 67604 = (1843.9648684694, -228.95189910969, -916)
pat = struct.pack("<ddd", 1843.9648684694, -228.95189910969, -916.0)
hits = [m.start() for m in re.finditer(re.escape(pat), p)]
print("node 67604 triple hits:", [hex(h) for h in hits[:6]])
# element 302870 refs (70393, 70098, 70097) as u32s
for seq in ([70393, 70098, 70097], [70098, 70393, 70097], [70393, 70395, 68912], [70098, 70393, 68911]):
    pat = b"".join(struct.pack("<I", v) for v in seq)
    h2 = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"refs {seq}: {[hex(h) for h in h2[:6]]}")
