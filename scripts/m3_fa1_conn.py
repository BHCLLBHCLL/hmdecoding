import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, find_elem_segments, u32, u16, is_const
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/frame_assembly_1.hm')
comp = {}
for line in open('output/m3_fa1_elemcomp.log', encoding='utf-8'):
    t = line.split()
    if len(t) == 4 and t[0] == 'E':
        comp[int(t[1])] = int(t[2])
# 找 comp=3,5,12 的元素 (前几个)
targets = {}
for eid, c in comp.items():
    if c in (3, 5, 12) and c not in targets:
        targets[c] = eid
print('target comp -> eid:', targets)
# 在 payload 中找这些 eid 的记录并 dump
segs = find_elem_segments(p)
for (sh, segid, cfg71, cnt, X, Y) in segs:
    if X != 3: continue
    for off in range(sh + 16, sh + 80):
        if is_const(u32(p, off)):
            rec = off; seen = 0
            while rec is not None and seen < cnt:
                eid = u32(p, rec + 4)
                if eid in targets.values():
                    fields = [u32(p, rec + o) for o in range(0, 56, 4)]
                    print('seg%d eid=%d comp=%d fields=%s' % (segid, eid, comp.get(eid), fields))
                seen += 1
                j = p.find(b'\xf5\x1f', rec + 4, min(rec + 200, len(p) - 2))
                nxt = None
                while j >= 0:
                    if is_const(u32(p, j)): nxt = j; break
                    j = p.find(b'\xf5\x1f', j + 1, min(rec + 200, len(p) - 2))
                rec = nxt
            break
