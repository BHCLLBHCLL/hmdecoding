"""v17 全面探查: 所有 e503 段头 + eid=365000 真实记录位置 + 235 记录归属."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, is_const, find_node_section_struct

p = open("output/ground_truth/v17_payload.bin", "rb").read()

# 行号映射
ns_list = [ens for ens in find_node_section_struct(p, multi=True) if ens[1] >= 50]
row_of = {}
row = 0
for cfg in sorted(ns_list, key=lambda s: s[2]):
    hi, count, base2, stride, idoff, chain = cfg
    for k in range(count):
        nid = u32(p, base2 + k * stride + idoff)
        row += 1
        row_of[nid] = row

# 1) 段 300001 区域内所有 e503 头 (不限 X/Y)
print("== all e503 headers in [44267255, 44298000]:")
start = 44260000
while True:
    i = p.find(b"\xe5\x03\x00\x00", start, 44298000)
    if i < 0:
        break
    segid, cfg71, cnt, X, Y = u32(p, i+4), u32(p, i+8), u32(p, i+12), u32(p, i+16), u32(p, i+20)
    print(f"  @{i} segid={segid} cfg71={cfg71} cnt={cnt} X={X} Y={Y}")
    start = i + 1

# 2) eid=365000 rows 序列搜索
rows = [row_of[n] for n in (701993, 702237, 701994, 702241)]
print("\neid=365000 rows:", rows)
import struct, itertools
found = []
for perm in itertools.permutations(rows):
    seq = b"".join(struct.pack("<I", r) for r in perm)
    j = p.find(seq)
    while j >= 0:
        found.append((j, perm))
        j = p.find(seq, j + 1)
for j, perm in sorted(found):
    print(f"  seq@{j}: {perm}")

# 3) 235 family-1 记录的 eid 范围 (段 300001 区域)
lo, hi = 44267255, 44284291
eids = []
j = lo
while True:
    j = p.find(b"\xf5\x1f", j, hi)
    if j < 0:
        break
    if is_const(u32(p, j)):
        flag = u32(p, j + 28)
        cfg = flag >> 16
        if 300 <= cfg <= 500 and (flag & 0xFFFF) == 0:
            eids.append((u32(p, j + 18), cfg - 256))
    j += 1
print(f"\nregion 300001 family-1 records: {len(eids)}, eid range {min(e[0] for e in eids)}..{max(e[0] for e in eids)}")
print("  first 10:", eids[:10])
print("  last 5:", eids[-5:])

# 4) oracle eid 集合核对
f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()
in_gt = sum(1 for e in eids if e[0] in gt)
print(f"  eid in oracle: {in_gt}/{len(eids)}")
print(f"  eid 365000/365001/365002 in oracle: {365000 in gt}, {365001 in gt}, {365002 in gt}")
