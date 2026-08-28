"""诊断 _parse_a_geom 在 wing_section_complete 上的进度."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, find_elem_segments, parse_nodes

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

MARK = b"\xe4\x0b\x04\x1a"
for sh, segid, cfg71, cnt, X, Y in find_elem_segments(p):
    if X != 3:
        continue
    print(f"\n== seg@{sh} cfg71={cfg71} cnt={cnt} X={X} Y={Y}")
    hits = []
    j = sh
    hi = 91338 if sh == 56330 else 129933
    while True:
        j = p.find(MARK, j, hi)
        if j < 0:
            break
        hits.append(j); j += 1
    print(f"  MARK hits: {len(hits)}")
    # 前 3 条的 eid/节点提取
    for k in range(min(3, len(hits))):
        rec = hits[k]
        eid = u32(p, rec + 36)
        nds = []
        rc = len(n1)
        for i in range(8):
            r = u32(p, rec + 48 + 4 * i) >> 16
            if not (1 <= r <= rc):
                break
            nds.append(r)
        print(f"  rec{k}@{rec}: eid={eid} nds={nds}")
    # 间距统计
    diffs = [b - a for a, b in zip(hits, hits[1:])]
    from collections import Counter
    print("  spacing dist:", Counter(diffs).most_common(5))
