import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, u16, find_elem_segments, is_const
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/cover.hm')
segs = find_elem_segments(p)
def first_rec(sh):
    for off in range(sh + 16, sh + 80):
        if is_const(u32(p, off)):
            return off
    return None
# seg1 (comp1) first rec, seg2 (comp2) first rec
r1 = first_rec(segs[0][0])
r2 = first_rec(segs[1][0])
print('seg1 rec @%d, seg2 rec @%d' % (r1, r2))
# 逐字段对比 (u32 @+4..+56)
print('off  seg1    seg2')
for off in range(4, 56, 4):
    a = u32(p, r1 + off); b = u32(p, r2 + off)
    mark = ' <== DIFF' if a != b else ''
    print('+%2d  %-7d %-7d%s' % (off, a, b, mark))
