import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]

# all record quadruples from the 0x70241FF5 stream
c = struct.pack("<I", 0x70241FF5)
recs = {}
for o in [m.start() for m in re.finditer(re.escape(c), p)]:
    s = o - 0x20
    if s >= 0 and u32(s) == 0 and u32(s+4) == 0x01680000:
        quad = tuple(u32(s + 8 + i*4) for i in range(4))
        recs[s] = quad
print("records:", len(recs))

# GT map from log
gt = {}
for line in open("output/ground_truth/elem_all.log", encoding="utf-8").read().splitlines()[1:]:
    parts = line.split()
    if len(parts) == 5:
        gt[int(parts[0])] = tuple(int(x) for x in parts[1:5])
print("GT elements:", len(gt))

# match: GT quad -> record position
q2s = {}
for s, quad in recs.items():
    q2s.setdefault(quad, []).append(s)

matched = 0
mapping = {}
unmatched = []
for eid, quad in gt.items():
    hits = q2s.get(quad, [])
    if hits:
        mapping[eid] = hits[0]
        matched += 1
    else:
        unmatched.append(eid)
print("matched:", matched, "unmatched:", len(unmatched))
print("unmatched sample:", unmatched[:20])

# check record->elem id field: for matched, is there a relationship between record pos and elem id?
import collections
rel = []
for eid, s in mapping.items():
    rel.append((eid, s))
print("first 10 matched (elem_id, record_off):", rel[:10])
# distribution of record offsets per element id — sorted?
print("matched eids sorted by record offset (first 15):", [e for e, s in sorted(rel, key=lambda x: x[1])][:15])
