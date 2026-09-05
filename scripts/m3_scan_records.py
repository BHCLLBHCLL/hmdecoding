import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u16, u32
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')
# 扫描 collector 记录: 3 u32 头 {19, type, name_len} + 名称@+12 (db 11.05)
found = []
for i in range(0, min(len(p), 8_000_000) - 20, 4):
    if u32(p, i) != 19:
        continue
    N = u32(p, i + 8)
    if not (2 <= N <= 100):
        continue
    s = p[i + 12:i + 12 + (N - 1)]
    if len(s) >= 2 and all(32 <= b < 127 for b in s):
        found.append((i, N, s.decode('ascii')))
recs = [(off, nm, N) for (off, N, nm) in found if len(nm) >= 3]
print('collector records found:', len(recs))
prev = None
for off, nm, N in recs:
    gap = (off - prev) if prev is not None else 0
    print('@%d name=%-22s N=%d (gap=%d)' % (off, nm, N, gap))
    prev = off
