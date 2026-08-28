"""找 truck eid 重叠来源: 哪些段的 eid 与其他段冲突."""
import sys
from collections import defaultdict, Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, d64, find_node_section, parse_nodes,
                     _parse_a_type, find_elem_segments)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

segs = find_elem_segments(p)
seg_eids = {}
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if got:
        seg_eids[segid] = set(got.keys())

# 每段 eid 与"前面所有段"重叠
prev = set()
overlaps = []
for segid in sorted(seg_eids, key=lambda s: segs[[x[1] for x in segs].index(s)][0]):
    cur = seg_eids[segid]
    dup = cur & prev
    if dup:
        overlaps.append((segid, len(cur), len(dup), sorted(dup)[:6]))
    prev |= cur
print(f"segs with eid overlap: {len(overlaps)}/{len(seg_eids)}")
for o in overlaps:
    print("  ", o)

# 汇总: 每个 eid 出现次数
all_eids = Counter()
for eids in seg_eids.values():
    all_eids.update(eids)
dups = {e: c for e, c in all_eids.items() if c > 1}
print(f"\nduplicated eids: {len(dups)} (total extra {sum(c-1 for c in dups.values())})")
if dups:
    ex = sorted(dups.items(), key=lambda x: -x[1])[:10]
    print("  top dups:", ex)
