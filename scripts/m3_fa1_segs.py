import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, find_elem_segments, u32, u16, is_const
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/frame_assembly_1.hm')
segs = find_elem_segments(p)
print('segs:', [(s[1], s[4], s[5], s[3]) for s in segs][:20])
# 第一个 X=2 段的记录 + oracle comp
# 加载 oracle 映射
comp = {}
for line in open('output/m3_fa1_elemcomp.log', encoding='utf-8'):
    t = line.split()
    if len(t) == 4 and t[0] == 'E':
        comp[int(t[1])] = int(t[2])
print('oracle comp map size', len(comp), 'sample', list(comp.items())[:5])
# 走第一个段记录, 打印字段 + comp
for (sh, segid, cfg71, cnt, X, Y) in segs[:3]:
    if X == 3:
        # A 型
        for off in range(sh + 16, sh + 80):
            if is_const(u32(p, off)):
                rec = off; seen = 0
                while rec is not None and seen < min(cnt, 3):
                    eid = u32(p, rec + 4)
                    # 记录字段
                    fields = [u32(p, rec + o) for o in range(0, 48, 4)]
                    print('A seg%d eid=%d comp=%s fields=%s' % (segid, eid, comp.get(eid), fields))
                    seen += 1
                    j = p.find(b'\xf5\x1f', rec + 4, min(rec + 200, len(p) - 2))
                    nxt = None
                    while j >= 0:
                        if is_const(u32(p, j)): nxt = j; break
                        j = p.find(b'\xf5\x1f', j + 1, min(rec + 200, len(p) - 2))
                    rec = nxt
                break
