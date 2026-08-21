import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]

c = struct.pack("<I", 0x70241FF5)
offs = [m.start() for m in re.finditer(re.escape(c), p)]
print("0x70241FF5 hits:", len(offs), "first:", [hex(o) for o in offs[:10]], "last:", [hex(o) for o in offs[-5:]])
# records: constant at +0x20 → record start = off - 0x20
starts = [o - 0x20 for o in offs]
print("record starts:", [hex(s) for s in starts[:10]])
# check record structure: +0x04 should be 0x01680000, +0x24 index, +0x28 = (index<<16)|2
ok4 = ok28 = 0
idx_vals = []
for s in starts:
    if u32(s + 4) == 0x01680000: ok4 += 1
    idx = u32(s + 0x24)
    idx_vals.append(idx)
    if u32(s + 0x28) == ((idx << 16) | 2): ok28 += 1
print(f"records={len(starts)} +0x04=0x01680000: {ok4}, +0x28=(idx<<16|2): {ok28}")
print("idx range:", min(idx_vals), "..", max(idx_vals))
print("first record:", [u32(starts[0] + i*4) for i in range(13)])
print("record 100:", [u32(starts[100] + i*4) for i in range(13)])
