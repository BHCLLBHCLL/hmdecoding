import gzip, struct, re
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def f32(off): return struct.unpack_from("<f", p, off)[0]
pat = struct.pack("<f", -916.0)
offs = [m.start() for m in re.finditer(re.escape(pat), p)]
print("f32 -916.0 hits:", len(offs))
if offs:
    print("first 20:", [hex(o) for o in offs[:20]])
    print("last 10:", [hex(o) for o in offs[-10:]])
    # spacing histogram
    from collections import Counter
    gaps = Counter(offs[i+1] - offs[i] for i in range(len(offs)-1))
    print("gaps:", gaps.most_common(8))
# dump region 0x194e00..0x195040
print()
for off in range(0x194e00, 0x195040, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"0x{off:05x}  {hexs}  {ascii_}")
