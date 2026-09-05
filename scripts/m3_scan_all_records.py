import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u16, u32

p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')

def printable(b):
    b = b.split(bytes([0]))[0]
    return len(b) > 0 and all(32 <= x < 127 for x in b) and any(65 <= x <= 122 for x in b)

recs = []
for i in range(0, len(p) - 16, 1):
    if u32(p, i) == 19 and u32(p, i + 4) == 0:
        nl = u32(p, i + 8)
        if 2 <= nl <= 128:
            name = bytes(p[i + 12:i + 12 + nl])
            if printable(name):
                recs.append((i, nl, name.split(bytes([0]))[0]))

for i, nl, name in recs:
    print('%d  nl=%d  %r' % (i, nl, name.decode('latin1')))
print('TOTAL', len(recs))
