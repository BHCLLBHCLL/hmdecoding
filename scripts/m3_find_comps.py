import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, u32, u16, d64
p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/cover.hm')
print('payload', len(p))
for name in (b'shells', b'IMPRINT1', b'EXTEND'):
    i = p.find(name)
    print('--- name=%s at offset %d' % (name, i))
    if i >= 0:
        # dump 前后 64 字节 u32 视角
        base = i - 32
        for o in range(base, min(base + 128, len(p)), 4):
            v = u32(p, o)
            if o < i:
                print('  @%d u32=%d  ascii=%s' % (o, v, p[o:o+4]))
            else:
                # 打印名字后字节 (可能是记录结构)
                if i <= o < i + 72:
                    print('  @%d u32=%d' % (o, v))
