import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, u16, find_elem_segments, is_const
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/cover.hm')
segs = find_elem_segments(p)
# 找第一个元素段 (seg1) 的第一条记录
sh, segid, cfg71, cnt, X, Y = segs[0]
print('seg1:', segs[0], 'sh=%d' % sh)
for off in range(sh + 16, sh + 80):
    if is_const(u32(p, off)):
        rec = off
        break
print('first rec @%d' % rec)
# dump 记录 100 字节
for o in range(rec, rec + 100, 4):
    v = u32(p, o)
    print('@%d u32=%-10d u16=%d,%d ascii=%r' % (o, v, u16(p,o), u16(p,o+2), p[o:o+4]))
