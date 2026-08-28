"""v17 深入: Y=2 段 eid 列表结构 + config 1/60 记录 + 131684 完整 core."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section_struct, find_elem_segments

p = open("output/ground_truth/v17_payload.bin", "rb").read()
ns_list = []
for ens in find_node_section_struct(p, multi=True):
    if ens[1] >= 50:
        ns_list.append(ens)
row_map = {}
row = 0
for cfg in sorted(ns_list, key=lambda s: s[2]):
    hi, count, base2, stride, idoff, chain = cfg
    for k in range(count):
        rec = base2 + k * stride
        if rec + stride > len(p):
            break
        nid = u32(p, rec + idoff)
        x = d64(p, rec + 12)
        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9):
            break
        row += 1
        row_map[row] = nid
row_of = {v: k for k, v in row_map.items()}
print(f"row 36402 -> nid {row_map.get(36402)}  (期待 2000000)")
print(f"row_of(2000000) = {row_of.get(2000000)}")

def dump(pos, lo, hi, label, rowmark=True):
    print(f"\n== {label} @ {pos}")
    for off in range(lo, hi, 4):
        q = pos + off
        if q < 0 or q + 4 > len(p):
            continue
        v = u32(p, q)
        u = (u16(p, q), u16(p, q + 2))
        mark = " <CONST>" if v == 0x70241FF5 else ""
        if u[1] == 701:
            mark += " <701>"
        if u[0] == 701:
            mark += " <701@lo>"
        if rowmark and 1 <= v <= 354176 and row_map.get(v) is not None and v > 100:
            mark += f" <row{v}->nid{row_map[v]}>"
        print(f"  {off:+5d}: {p[q:q+4].hex(' ')}  u32={v:<11d} u16={u}{mark}")

# 1) seg 100004 Y=2 eid 列表 + CONST core 完整结构 (131766 hit @38059451)
dump(38059451, -64, 128, "seg100004 Y=2 eid-list (131766 in list)")

# 2) 131766 (config 1, node 617771 row 250985) / 131757 (config 60) 存储位置
for eid in (131757, 131766, 131767, 131764, 131765, 589137, 589150, 589700):
    pat = struct.pack("<I", eid)
    pos = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        pos.append(j); j += 1
    print(f"\neid={eid}: hits={pos[:8]}")

# 3) 131684 完整 core (容器 @31997671, core rows 从 +64 开始)
dump(31997671, 48, 144, "seg2000486 容器 131684 core rows")

# 4) seg 6500115 header
segs = sorted(find_elem_segments(p), key=lambda s: s[0])
for s in segs:
    if s[1] in (6500115,):
        print(f"\nseg 6500115: sh={s[0]} cfg={s[2]} cnt={s[3]} X={s[4]} Y={s[5]}")
        print("  header:", p[s[0]:s[0]+24].hex(' '))
        # 下一段
        for s2 in segs:
            if s2[0] > s[0]:
                print(f"  next seg @ {s2[0]} ({s2[0]-s[0]} bytes later) segid={s2[1]}")
                break
