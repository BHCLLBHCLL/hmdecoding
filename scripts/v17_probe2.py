"""v17 SHORT 段记录结构探查: 300001 首记录(eid=365000?), 2000486(3912279), 6500113(B型)."""
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
print("row_map rows:", row)

# oracle: eid=365000 nodes=701993 702237 701994 702241; eid=144234 nodes=427020 427063 425991 425983
for eid, nodes in [(365000, [701993, 702237, 701994, 702241]),
                   (144234, [427020, 427063, 425991, 425983])]:
    print(f"eid={eid} rows:", [row_of.get(n) for n in nodes])

def dump(pos, lo, hi, label):
    print(f"\n== {label} @ {pos}")
    for off in range(lo, hi, 4):
        v = u32(p, pos + off)
        note = " CONST" if is_const(v) else ""
        print(f"  {off:+4d}: {p[pos+off:pos+off+4].hex()} u32={v:>10d} u16=({u16(p,pos+off)},{u16(p,pos+off+2)}){note}")

# 段 300001: sh=44267255, 区域内首个 const 记录
sh = 44267255
j = p.find(b"\xf5\x1f", sh + 16, sh + 200)
while j >= 0 and not is_const(u32(p, j)):
    j = p.find(b"\xf5\x1f", j + 1, sh + 200)
print("seg 300001 first const record at", j)
dump(j, 0, 80, "seg300001 rec1 (storage=365000?)")

# 段 2000486: sh=31997647
sh = 31997647
j = p.find(b"\xf5\x1f", sh + 16, sh + 200)
while j >= 0 and not is_const(u32(p, j)):
    j = p.find(b"\xf5\x1f", j + 1, sh + 200)
print("seg 2000486 first const record at", j)
dump(j, 0, 80, "seg2000486 rec1 (storage=3912279?)")

# 段 6500113: sh=38005415 (B型 OK), dump sh+24 起
dump(38005415 + 24, 0, 64, "seg6500113 B-type rec1")

# 段 300001 区域内第 4 个 const 记录 (eid=305862 family-1)
j2 = 44267255
cnt = 0
k = j2
while True:
    k = p.find(b"\xf5\x1f", k + 1, 44284291)
    if k < 0:
        break
    if is_const(u32(p, k)):
        cnt += 1
        if cnt == 4:
            dump(k, 0, 64, "seg300001 rec4 (family-1 eid=305862)")
            break
