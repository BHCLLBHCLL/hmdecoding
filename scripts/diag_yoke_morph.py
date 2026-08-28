"""yoke/Morph_Adhesive 记录结构: @+4 vs @+8 关系."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const

for path, name in [
    (r"C:\Program Files\Altair\2019\tutorials\hm\yoke.hm", "yoke"),
    (r"C:\Program Files\Altair\2019\tutorials\hm\Morph_Adhesive_Layers.hm", "Morph_Adhesive_Layers"),
    (r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_3.hm", "frame_assembly_3"),
]:
    p = load_payload(path)
    segs = find_elem_segments(p)
    store_hi_same = 0
    total = 0
    v8hi = Counter()
    v12 = Counter()
    v4_range = []
    sample = None
    for sh, segid, cfg71, cnt, X, Y in segs:
        if X != 3:
            continue
        anchor = None
        for s in range(sh + 16, sh + 80):
            if is_const(u32(p, s)):
                anchor = s; break
        if anchor is None:
            continue
        rec = anchor
        for k in range(cnt):
            total += 1
            v4 = u32(p, rec + 4)
            hi = u32(p, rec + 8) >> 16
            v8hi[hi] += 1
            v12[u16(p, rec + 12)] += 1
            if v4 == hi:
                store_hi_same += 1
            if sample is None:
                sample = (segid, Y, [u32(p, rec + 4*i) for i in range(12)])
            nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
            while nxt >= 0:
                if is_const(u32(p, nxt)): break
                nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
            if nxt < 0: break
            rec = nxt
    print(f"\n=== {name} === 记录数={total} @+4==@+8hi: {store_hi_same}/{total}")
    print(f"  @+8hi 分布 top: {v8hi.most_common(5)}")
    print(f"  u16(+12) 分布 top: {v12.most_common(5)}")
    print(f"  样本记录: seg={sample[0]} Y={sample[1]} u32={sample[2]}")
