"""统计 wing_section seg@56330 所有 MARK hit 的 (eid, +4, +16, +24) 特征."""
import sys, gzip
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
MARK = b"\xe4\x0b\x04\x1a"

rows = []
j = 56330
while True:
    j = p.find(MARK, j, 91338)
    if j < 0:
        break
    eid = u32(p, j + 36)
    rows.append((j, eid, u32(p, j + 4), hex(u32(p, j + 16)), hex(u32(p, j + 24))))
    j += 1
print(f"total hits: {len(rows)}")
c4 = Counter(r[2] for r in rows)
print("+4 dist:", dict(c4))
c24 = Counter(r[4] for r in rows)
print("+24 dist:", dict(c24))
c16 = Counter(r[3] for r in rows)
print("+16 dist:", dict(c16))

# eid 连续性
eids = [r[1] for r in rows if 0 < r[1] < 10000000]
print(f"eids: {len(eids)} range {min(eids)}..{max(eids)}")
gap = [(a, b) for a, b in zip(eids, eids[1:]) if b - a != 1]
print(f"eid gaps: {gap[:10]}")
