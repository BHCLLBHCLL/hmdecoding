import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, u16
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')
for name in [b'Front_Truss_1', b'M_^_6_11', b'P_^_6_11_HEX', b'C_Spotweld_1', b'C_^_6_11_HEX']:
    i = p.find(name)
    print('=== %s at %d' % (name, i))
    if i < 0: continue
    # dump 名字前 32 字节 (u16 视角) 找记录头/段头
    for o in range(i - 32, i, 2):
        v = u16(p, o)
        ch = chr(v) if 32 <= v < 127 else '.'
        print('  @%d u16=%-6d %s' % (o, v, ch))
