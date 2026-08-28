"""v17 seg 100026 完整记录 dump + eid 行号搜索 + 假设检验."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, is_const, find_node_section_struct

p = open("output/ground_truth/v17_payload.bin", "rb").read()

ns_list = [ens for ens in find_node_section_struct(p, multi=True) if ens[1] >= 50]
row_of = {}
nid_of = {}
row = 0
for cfg in sorted(ns_list, key=lambda s: s[2]):
    hi, count, base2, stride, idoff, chain = cfg
    for k in range(count):
        nid = u32(p, base2 + k * stride + idoff)
        row += 1
        row_of[nid] = row
        nid_of[row] = nid

f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()

for v in (589141, 589271, 517663, 263874, 589209, 131704, 64921, 64853, 64983):
    print(f"eid {v} in oracle: {v in gt}")
print("nid(129939)=", nid_of.get(129939), "nid(129940)=", nid_of.get(129940))
print("nid(222244)=", nid_of.get(222244), "nid(222243)=", nid_of.get(222243))
print("nid(183520)=", nid_of.get(183520), "nid(183523)=", nid_of.get(183523))

# seg 100026 完整记录 (len=212)
print("\n== seg 100026 full record @ 40564275 (len 212):")
for off in range(0, 212, 4):
    v = u32(p, 40564275 + off)
    note = " CONST" if is_const(v) else ""
    print(f"  {off:+4d}: {p[40564275+off:40564275+off+4].hex()} u32={v:>10d} u16=({u16(p,40564275+off)},{u16(p,40564275+off+2)}){note}")

# eid=144234 的行号出现位置
rows144 = [row_of[n] for n in (427020, 427063, 425991, 425983)]
rows365 = [row_of[n] for n in (701993, 702237, 701994, 702241)]
print("\neid=144234 rows:", rows144)
for r in rows144:
    hits = []
    j = 0
    while True:
        j = p.find(struct.pack("<I", r), j)
        if j < 0:
            break
        hits.append(j)
        j += 1
    print(f"  row {r}: {len(hits)} hits: {hits[:12]}")
print("eid=365000 rows:", rows365)
for r in rows365:
    hits = []
    j = 0
    while True:
        j = p.find(struct.pack("<I", r), j)
        if j < 0:
            break
        hits.append(j)
        j += 1
    print(f"  row {r}: {len(hits)} hits: {hits[:12]}")
