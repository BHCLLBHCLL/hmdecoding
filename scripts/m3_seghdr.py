import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, u16, find_elem_segments
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/cover.hm')
for (sh, segid, cfg71, cnt, X, Y) in find_elem_segments(p):
    vals = [u32(p, sh + o) for o in range(0, 56, 4)]
    print('seg%d sh=%d cnt=%d X=%d Y=%d hdr=%s' % (segid, sh, cnt, X, Y, vals))
