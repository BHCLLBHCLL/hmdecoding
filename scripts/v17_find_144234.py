"""定位元素 144234 的真实记录: 检查各 u32 hit 周围, 按节点行号搜索."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, is_const

p = open("output/ground_truth/v17_payload.bin", "rb").read()
# 需要行号: 从节点段重建 (行号 → nid)
from decoder import find_node_section_struct
ns_list = []
for ens in find_node_section_struct(p, multi=True):
    if ens[1] < 50:
        continue
    ns_list.append(ens)
row_of = {}
row = 0
for cfg in sorted(ns_list, key=lambda s: s[2]):
    hi, count, base2, stride, idoff, chain = cfg
    for k in range(count):
        rec = base2 + k * stride
        nid = u32(p, rec + idoff)
        row += 1
        row_of[nid] = row

rows = [row_of[n] for n in (427020, 427063, 425991, 425983)]
print("element 144234 node rows:", rows)

# 在全载荷搜索这些行号的任意连续 4 序列 (含乱序)
import struct, itertools
for perm in itertools.permutations(rows):
    seq = b"".join(struct.pack("<I", r) for r in perm)
    j = p.find(seq)
    if j >= 0:
        print(f"  seq {perm} -> {j}")

# 各 hit 位置周围
for pos in (41662951, 41716987, 41756691, 41760951, 46528845, 70855730):
    print(f"\n== hit @{pos}")
    for off in range(-24, 48, 4):
        v = u32(p, pos + off)
        note = " CONST" if is_const(v) else ""
        mark = " <--ROW" if v in rows else ""
        print(f"  {off:+4d}: {p[pos+off:pos+off+4].hex()} u32={v:>10d}{note}{mark}")
