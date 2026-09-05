import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u16
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')
# MAT 名 "M_^_6_11" @2352127
base = 2352127
print('=== MAT 名前 200 字节 ===')
for o in range(base - 200, base, 2):
    v = u16(p, o)
    ch = chr(v) if 32 <= v < 127 else '.'
    if v != 0 or ch != '.':
        print('  @%d u16=%-6d %s' % (o, v, ch))
print('=== MAT 名后 100 字节 ===')
for o in range(base, base + 100, 2):
    v = u16(p, o)
    ch = chr(v) if 32 <= v < 127 else '.'
    if v != 0 or ch != '.':
        print('  @%d u16=%-6d %s' % (o, v, ch))
