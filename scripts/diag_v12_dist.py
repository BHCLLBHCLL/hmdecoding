"""@+12 与 @+8lo 分布: 区分「@+8hi=eid」vs「@+4=eid」的判别字段."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

cases = [
    (r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_3.hm", "fa3(用@+8hi)"),
    (r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly_1.hm", "fa1"),
    (r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_4.hm", "fa4"),
    (r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm", "truck"),
    (r"C:\Program Files\Altair\2019\tutorials\hm\yoke.hm", "yoke(用@+4)"),
    (r"C:\Program Files\Altair\2019\tutorials\hm\Morph_Adhesive_Layers.hm", "Morph(用@+4)"),
]

for path, name in cases:
    p = load_payload(path)
    segs = find_elem_segments(p)
    v12 = Counter()
    v8lo = Counter()
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
        for k in range(min(cnt, 2000)):
            v12[u16(p, rec + 12)] += 1
            v8lo[u32(p, rec + 8) & 0xFFFF] += 1
            nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
            while nxt >= 0:
                if is_const(u32(p, nxt)): break
                nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
            if nxt < 0: break
            rec = nxt
    print(f"\n{name}: u16(+12)={dict(v12.most_common(8))}  @+8lo={dict(v8lo.most_common(8))}")
