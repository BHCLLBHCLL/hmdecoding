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

matched = sum(1 for k in records if records[k] == gt.get(k))
print("records:", len(records), "direct idx==eid matches:", matched)
# show GT 40..50 vs records 40..50
for k in range(40, 51):
    print(f"  idx {k}: record={records.get(k)}  gt={gt.get(k)}")
# any permutation match?
import itertools
perm_ok = 0
for k in records:
    if set(records[k]) == set(gt.get(k, ())):
        perm_ok += 1
print("set-equal matches:", perm_ok)
