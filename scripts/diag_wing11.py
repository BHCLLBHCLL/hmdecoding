"""统计标准记录 (+4==8) 的 eid/节点验证失败原因."""
import sys, gzip
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
MARK = b"\xe4\x0b\x04\x1a"
rc = 1042

for sh, hi in ((56330, 91338), (91338, 129933)):
    std = []
    j = sh + 24
    prev = None
    while j < hi:
        j = p.find(MARK, j, hi)
        if j < 0:
            break
        if prev is not None and not (68 <= j - prev <= 80):
            j += 1
            continue
        if u32(p, j + 4) == 8:
            std.append((j, u32(p, j + 36)))
            prev = j
        j += 1
    print(f"seg@{sh}: standard recs {len(std)}")
    eids = [e for _, e in std]
    ok_eid = [x for x in eids if 0 < x < 10_000_000]
    print(f"  eid valid: {len(ok_eid)}/{len(eids)}")
    print(f"  eid sample: {eids[:8]} ... {eids[-4:]}")
    # eid 连续性
    gaps = [(a, b) for a, b in zip(eids, eids[1:]) if b - a != 1]
    print(f"  eid gaps: {len(gaps)} sample {gaps[:6]}")
