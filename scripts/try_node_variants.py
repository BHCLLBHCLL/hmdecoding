import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])

def find(pat, label):
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"{label}: {len(hits)} hits at {[hex(h) for h in hits[:6]]}")
    return hits

# variant patterns for elem 198 nodes (294,292,291,293) = 0x126, 0x124, 0x123, 0x125
n1, n2, n3, n4 = 294, 292, 291, 293
for gap in (4, 8, 12):
    for perm, name in [((0,1,2,3),"fwd"), ((3,2,1,0),"rev"), ((0,3,2,1),"3120")]:
        pat = b""
        for i in perm:
            pat += struct.pack("<I", (n1, n2, n3, n4)[i])
            if perm.index(i) < 3:
                pat += bytes(gap - 4) if gap > 4 else b""
        find(pat, f"gap{gap} {name}")
# 2-byte ids?
for perm, name in [((0,1,2,3),"fwd"), ((3,2,1,0),"rev")]:
    pat = b"".join(struct.pack("<H", (n1, n2, n3, n4)[i]) for i in perm)
    find(pat, f"u16 {name}")
# with 0x70241FF5 nearby: element records contain constant at +0x20, nodes at +8..+0x14
# maybe nodes stored as u32 minus something, or +offset. Check 294 in payload:
h294 = [m.start() for m in re.finditer(re.escape(struct.pack("<I", 294)), p)]
print("u32 294 hits:", len(h294), [hex(h) for h in h294[:10]])
