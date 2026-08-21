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

# cross-match: any record quad == any GT quad (exact or as set)?
gt_by_set = {}
for eid, q in gt.items():
    gt_by_set.setdefault(tuple(sorted(q)), []).append(eid)
exact = 0
setm = 0
for k, q in records.items():
    if q in gt.values():
        exact += 1
    if tuple(sorted(q)) in gt_by_set:
        setm += 1
print(f"exact cross matches: {exact}, set cross matches: {setm}")
# value overlap statistics
rec_vals = set(v for q in records.values() for v in q)
gt_vals = set(v for q in gt.values() for v in q)
print("record quads value range:", min(rec_vals), "-", max(rec_vals), "count:", len(rec_vals))
print("GT quads value range:", min(gt_vals), "-", max(gt_vals), "count:", len(gt_vals))
print("overlap:", len(rec_vals & gt_vals))
print("record-only sample:", sorted(rec_vals - gt_vals)[:30])
print("GT-only sample:", sorted(gt_vals - rec_vals)[:30])
# do record quads look like GT quads of a SUBSET (e.g., first N elements)?
for n in (10, 20, 50, 100, 200):
    sub = set(v for eid in range(1, n+1) for v in gt[eid])
    print(f"GT elems 1..{n} value set size {len(sub)}; record values subset? {rec_vals <= sub}")
