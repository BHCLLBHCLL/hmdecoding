import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, u16
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')
# 段头模式: [u16 ptr][0][count][0][2][0][type_char] ... 更宽松: 找 count(>=1) 后紧跟 2 后紧跟大写字母
import collections
hits = collections.defaultdict(list)
for i in range(0, min(len(p), 8_000_000) - 14, 2):
    if u16(p, i+2) == 0 and 1 <= u16(p, i+4) <= 500 and u16(p, i+6) == 0 and u16(p, i+8) == 2 and u16(p, i+10) == 0:
        cnt = u16(p, i+4)
        tch = u16(p, i+12)
        if 32 <= tch < 127:
            hits[chr(tch)].append((i, cnt))
for ch, lst in sorted(hits.items()):
    if len(lst) >= 1:
        print('type=%r entries=%s' % (ch, [(i, c) for i, c in lst[:8]]))
