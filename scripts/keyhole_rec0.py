import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/keyhole.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
cp=76789
print('rec0 @',cp)
for off in range(0,56,4):
    v=u32(p,cp+off)
    print('  +%02d: %08x  (u16[%d]=%d u16[%d]=%d)'%(off,v,off,v&0xffff,off+2,v>>16))