"""v17 未覆盖 missing eid 的字节级搜索: 找到每个元素的真实记录位置."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, is_const, find_node_section_struct, find_elem_segments

p = open("output/ground_truth/v17_payload.bin", "rb").read()

f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()

MARK = b"\xf5\x1f\x24\x70"
cores = {}
j = 0
while True:
    j = p.find(MARK, j)
    if j < 0:
        break
    flag = u32(p, j + 28)
    cfg = flag >> 16
    if 300 <= cfg <= 500 and (flag & 0xFFFF) == 0:
        eid = u32(p, j + 18)
        rows = []
        k = j + 32
        while u32(p, k) != 0 and len(rows) < 12:
            rows.append(u32(p, k))
            k += 4
        if 1 <= len(rows) <= 12 and all(1 <= r <= 354175 for r in rows):
            cores[eid] = (cfg, tuple(rows))
    j += 1
missing = sorted(gt - set(cores))

# 已检测的嵌入 core (SHORT 段)
segs = sorted(find_elem_segments(p), key=lambda s: s[0])
short = [s for s in segs if s[5] != 2]
detected = set()
for sh, segid, cfg71, cnt, X, Y in short:
    hi = len(p)
    for s2 in segs:
        if s2[0] > sh:
            hi = s2[0]
            break
    j = sh
    while True:
        j = p.find(MARK, j, hi)
        if j < 0:
            break
        if is_const(u32(p, j)):
            for off in range(8, 400, 4):
                v = u16(p, j + off + 2)
                if v in (701, 686) and u16(p, j + off + 4) == 2596:
                    c0 = j + off - 8
                    detected.add(u32(p, c0 + 18))
                    break
        j += 1

uncovered = [e for e in missing if e not in detected]
print(f"missing total={len(missing)}, detected={len(detected & set(missing))}, uncovered={len(uncovered)}")
print("uncovered sample:", uncovered[:30])

# 对未覆盖 eid 做字节搜索
def find_all(eid, limit=6):
    hits = []
    pat = struct.pack("<I", eid)
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        hits.append(j)
        j += 1
        if len(hits) >= limit:
            break
    return hits

for eid in uncovered[:6]:
    hits = find_all(eid)
    print(f"\neid {eid}: hits={hits}")
    for h in hits[:3]:
        print(f"  @ {h}:")
        for off in range(-24, 40, 4):
            v = u32(p, h + off)
            note = " CONST" if is_const(v) else ""
            print(f"    {off:+4d}: {p[h+off:h+off+4].hex()} u32={v:>10d} u16=({u16(p,h+off)},{u16(p,h+off+2)}){note}")
