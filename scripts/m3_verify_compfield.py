import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, u16, find_elem_segments, is_const
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/cover.hm')
segs = find_elem_segments(p)
for (sh, segid, cfg71, cnt, X, Y) in segs:
    if X != 3: continue
    recs = []
    for off in range(sh + 16, sh + 80):
        if is_const(u32(p, off)):
            rec = off; seen = 0
            while rec is not None and seen < cnt:
                recs.append(rec); seen += 1
                j = p.find(b'\xf5\x1f', rec + 4, min(rec + 200, len(p) - 2))
                nxt = None
                while j >= 0:
                    if is_const(u32(p, j)): nxt = j; break
                    j = p.find(b'\xf5\x1f', j + 1, min(rec + 200, len(p) - 2))
                rec = nxt
            break
    if not recs: continue
    for rec in recs[:3] + recs[-1:]:
        e4 = u32(p, rec + 4)
        c44 = u32(p, rec + 44)
        print('seg%d rec@%d e4=%d u16@+10=%d @+44=%d' % (segid, rec, e4, u16(p, rec+10), c44))
