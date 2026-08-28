"""wing_section_complete seg@56330 复合记录边界分析: 找记录间距与行号."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
row_count = 1042

sh = 56330
# 找 CONST 或下一个元素段边界
hi = 91338
# 找 0x1a040be4 常量出现位置 (记录头标记?)
MARKS = [0x1a040be4, 0x0a040be6, 0x12040084]
import collections
pos_map = collections.defaultdict(list)
for m in MARKS:
    j = sh
    while True:
        j = p.find(m.to_bytes(4, "little"), j, hi)
        if j < 0:
            break
        pos_map[m].append(j)
        j += 1
for m, pos in pos_map.items():
    print(f"mark {m:#x}: {len(pos)} hits @ {pos[:12]}")

# 0x1a040be4 的间距
p1 = pos_map.get(0x1a040be4, [])
diffs = [b - a for a, b in zip(p1, p1[1:])]
print("0x1a040be4 spacing:", diffs[:12], "unique:", sorted(set(diffs))[:12])

# 若间距均匀, 记录边界
if len(diffs) > 3 and len(set(diffs)) == 1:
    stride = diffs[0]
    print(f"record stride = {stride}")
    # 对前 3 条记录 dump 行号区
    for k in range(3):
        rec = p1[k]
        print(f"\n== rec{k} @{rec} (rel {rec-sh}) ==")
        for off in range(-24, 140, 4):
            q = rec + off
            v = u32(p, q)
            a, b = u16(p, q), u16(p, q + 2)
            mark = ""
            if 1 <= a <= row_count:
                mark += f" <row{a}>"
            if 1 <= b <= row_count:
                mark += f" <row{b}>"
            print(f"  {off:+4d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({a},{b}){mark}")
