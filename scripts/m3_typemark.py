import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, u16
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')
# 搜段头模式: [7277][count][2][type_char] 其中 type_char in {'C','M','P','L','S','G'}
import collections
hits = collections.defaultdict(list)
for i in range(0, min(len(p), 8_000_000) - 8, 2):
    if u16(p, i) == 7277 and u16(p, i + 4) >= 1 and u16(p, i + 8) == 2:
        cnt = u16(p, i + 4)
        tch = u16(p, i + 12)
        ch = chr(tch) if 32 <= tch < 127 else '?'
        hits[ch].append((i, cnt))
for ch, lst in sorted(hits.items()):
    print('type=%r count=%d entries=%s' % (ch, len(lst), [(i, c) for i, c in lst[:6]]))
