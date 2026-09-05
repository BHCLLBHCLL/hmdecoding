import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, u16
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')
# 各类型首条名字偏移: comp=1293120(Front_Truss_1), mat=2352127(M_^_6_11), prop=2351449(P_^_6_11_HEX)
for label, name_off in [('COMP', 1293120), ('MAT', 2352127), ('PROP', 2351449)]:
    print('=== %s (name@%d) 前 64 字节 u16 ===' % (label, name_off))
    for o in range(name_off - 64, name_off, 2):
        v = u16(p, o)
        ch = chr(v) if 32 <= v < 127 else '.'
        print('  @%d u16=%-6d %s' % (o, v, ch))
