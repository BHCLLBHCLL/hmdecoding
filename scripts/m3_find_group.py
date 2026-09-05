import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u16, u32

p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')

# search for 'Spotweld' ascii
needle = b'Spotweld'
idx = p.find(needle)
print('Spotweld at', idx)
# dump around it
if idx >= 0:
    for o in range(-40, 40, 2):
        i = idx + o
        v = u16(p, i)
        ch = chr(v) if 32 <= v < 127 else '.'
        print('%+6d  %5d  0x%04x  %r' % (o, v, v, ch))

print()
print('===== bytes before prop@2351437 =====')
for o in range(-60, 8, 2):
    i = 2351437 + o
    v = u16(p, i)
    ch = chr(v) if 32 <= v < 127 else '.'
    print('%+6d  %5d  0x%04x  %r' % (o, v, v, ch))

print()
print('===== bytes before mat@2352115 (already seen) =====')
print()
print('===== search section markers: u16==997 or 1881415669 near end =====')
for i in range(2340000, len(p)-4, 2):
    if u16(p, i) == 997:
        print('997 @', i, u16(p,i+2), u16(p,i+4), u16(p,i+6))
