import gzip, struct

def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])

a = load("v1913_02_n4a")
b = load("v1913_03_t1")
print("n4a:", len(a), "t1:", len(b))
# diff with 8-byte alignment
regions = []
start = None
n = min(len(a), len(b))
for i in range(0, n, 8):
    if a[i:i+8] != b[i:i+8]:
        if start is None: start = i
    else:
        if start is not None:
            regions.append((start, i)); start = None
if start is not None: regions.append((start, n))
print("changed regions:", len(regions))
for s, e in regions:
    print(f"  0x{s:04x}..0x{e:04x} ({e-s:5d} bytes)")
# find the region that only EXISTS in t1 (element data) - t1 is longer?
print("size diff:", len(b) - len(a))
# dump the element-section candidate: new content near where node section ends
# n4a node section: node4 at 0x585, end 0x5cd; table at 0x624
# t1: locate node4 triple
import re
pat = struct.pack("<ddd", 0.0, 0.0, 10.0)
base = [m.start() for m in re.finditer(re.escape(pat), b)]
print("t1 node4 candidates:", [hex(x) for x in base])
for x in base:
    # check stride 72 for nodes 1-4 from this base
    ok = True
    for nid, (xx, yy, zz) in {1:(1.,2.,3.), 2:(10.,0.,0.), 3:(0.,10.,0.)}.items():
        r2 = x - (4 - nid) * 72
        v = struct.unpack_from("<ddd", b, r2)
        if abs(v[0]-xx) > 1e-9 or abs(v[1]-yy) > 1e-9 or abs(v[2]-zz) > 1e-9:
            ok = False
    if ok:
        print("  node4 TRUE at", hex(x), "node1 at", hex(x - 3*72))
        n1 = x - 3*72
        # dump after node4 record: element section?
        end = x + 72
        print(f"  after node4 record (0x{end:x}..0x{end+0x200:x}):")
        for off in range(end, end + 0x200, 16):
            chunk = b[off:off+16]
            print(f"    {off:04x}  {' '.join(f'{c:02x}' for c in chunk)}")
