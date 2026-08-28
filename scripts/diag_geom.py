"""诊断 geometry.hm 元素段 (0/4116)."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, parse_nodes, find_elem_segments, is_const
from collections import Counter

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\geometry.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
print("nodes:", len(n1), ns)
segs = find_elem_segments(p)
print("elem segs:", len(segs))
print("X:", Counter(s[4] for s in segs), "Y:", Counter(s[5] for s in segs).most_common(8), "cfg71:", Counter(s[2] for s in segs).most_common(8))
for s in sorted(segs, key=lambda s: -s[3])[:6]:
    print("  big:", s)
# 首个段 dump
if segs:
    sh, segid, cfg71, cnt, X, Y = sorted(segs, key=lambda s: -s[3])[0]
    print(f"\n== big seg @{sh} cfg71={cfg71} cnt={cnt} X={X} Y={Y} ==")
    for off in range(0, 100, 4):
        q = sh + off
        v = u32(p, q)
        mark = " <CONST>" if is_const(v) else ""
        print(f"  +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)}){mark}")
