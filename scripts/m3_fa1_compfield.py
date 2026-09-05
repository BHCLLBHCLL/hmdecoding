import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, find_elem_segments, u32, u16, is_const
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/frame_assembly_1.hm')
comp = {}
for line in open('output/m3_fa1_elemcomp.log', encoding='utf-8'):
    t = line.split()
    if len(t) == 4 and t[0] == 'E':
        comp[int(t[1])] = int(t[2])
segs = find_elem_segments(p)
# 打印每个段第一条记录的完整字段 (48B), 标注 comp
for (sh, segid, cfg71, cnt, X, Y) in segs:
    if X != 3: continue
    for off in range(sh + 16, sh + 80):
        if is_const(u32(p, off)):
            rec = off
            eid = u32(p, rec + 4)
            fields = [u32(p, rec + o) for o in range(0, 56, 4)]
            c = comp.get(eid)
            # 只看 @+20 与 @+44 (u16 高/低) 
            f20 = fields[5]; f44 = fields[11]
            print('seg%-2d eid=%-6d comp=%-2d @+20=%d(hi=%d) @+44=%d  @+8_hi=%d' % (
                segid, eid, c, f20, f20 >> 16, f44, fields[2] >> 16))
            break
