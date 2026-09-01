import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
for cp in [171276,171352,171428,171504]:
    print('=== @%d ==='%cp)
    for off in range(0,68,4):
        v=u32(p,cp+off)
        print('  +%02d: %08x (u16[+%d]=%d u16[+%d]=%d)'%(off,v,off,v&0xffff,off+2,v>>16))