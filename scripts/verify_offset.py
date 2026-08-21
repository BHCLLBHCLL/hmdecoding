import gzip, struct

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]

gt = {}
for line in open("output/ground_truth/elem_all.log", encoding="utf-8").read().splitlines()[1:]:
    parts = line.split()
    if len(parts) == 5:
        gt[int(parts[0])] = tuple(int(x) for x in parts[1:5])

records = {}
for i in range(0, len(p) - 0x30, 4):
    if u32(i) == 0 and u32(i+4) == 0x01680000:
        idx = u32(i + 0x24)
        if 1 <= idx <= 400:
            records[idx] = tuple(u32(i + 8 + j*4) for j in range(4))

OFF = 23
ok = 0
for k, quad in records.items():
    if k - 1 in gt and tuple(v + OFF for v in quad) == gt[k - 1]:
        ok += 1
print(f"verified with +{OFF} offset: {ok}/{len(records)}")
# show a few
for k in (2, 3, 43, 44, 100, 200, 400):
    quad = records[k]
    print(f"  rec idx {k}: {quad} -> +{OFF} = {tuple(v+OFF for v in quad)}  GT({k-1}) = {gt.get(k-1)}")
# find node section: how are nodes stored? check node row -> id mapping
# node section hypothesis: 52-byte records; find node (1,2,3) style triples for GT nodes
# check: node id 151 -> row 128 -> in the record stream, is node 151's COORDS at a 52-stride row indexed 128?
# Actually: check leg-style node records in 1d_elements: search for coordinate triple of a known node
# get coords of node 151 from oracle? not fetched; instead verify row structure: find the node section by searching for 52-byte-spaced triples of low ids
