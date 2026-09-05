import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, u16, d64
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/cover.hm')
# 组件段 ~111430..111760
for o in range(111420, 111760, 4):
    v = u32(p, o)
    asc = p[o:o+4]
    print('@%d u32=%-12d u16=%d,%d hex=%08x ascii=%r' % (o, v, u16(p,o), u16(p,o+2), v, asc))
