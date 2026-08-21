import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]

gt = {}
for line in open("output/ground_truth/elem_all.log", encoding="utf-8").read().splitlines()[1:]:
    parts = line.split()
    if len(parts) == 5:
        gt[int(parts[0])] = tuple(int(x) for x in parts[1:5])
print("GT(33):", gt[33], "GT(34):", gt[34])

# records: iterate payload, find all [0][0x01680000] patterns
hits = []
for i in range(0, len(p) - 16, 4):
    if u32(i) == 0 and u32(i+4) == 0x01680000 and u32(i+8) < 1000000 and u32(i+12) < 1000000:
        hits.append(i)
print("candidate records:", len(hits))
for h in hits[:6]:
    quad = tuple(u32(h + 8 + j*4) for j in range(4))
    idx = u32(h + 0x24)
    print(f"  @0x{h:x} quad={quad} idx={idx}")
# find the record whose quad == GT(33)
for h in hits:
    quad = tuple(u32(h + 8 + j*4) for j in range(4))
    if quad == gt[33]:
        print(f"GT(33) found at record 0x{h:x}, idx={u32(h+0x24)}")
# also: check if the record quads contain GT node VALUES in permuted order (same set)
for h in hits:
    quad = tuple(u32(h + 8 + j*4) for j in range(4))
    if set(quad) == set(gt[33]):
        print(f"GT(33) as SET at 0x{h:x} quad={quad} idx={u32(h+0x24)}")
# how many distinct quads
qs = set(tuple(u32(h + 8 + j*4) for j in range(4)) for h in hits)
print("distinct quads:", len(qs))
