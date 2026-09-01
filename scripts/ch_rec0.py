import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
cp=325785
print('channel rec0 @',cp)
for off in range(0,64,4):
    v=u32(p,cp+off)
    print('  +%02d: %08x'%(off,v))