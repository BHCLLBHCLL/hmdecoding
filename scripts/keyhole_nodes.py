import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/keyhole.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
row_count=550
cp=76789
print('rec0 scanning @+24..+44 for valid row refs (1..550):')
for off in range(24,44,4):
    v=u32(p,cp+off)
    print('  +%d: %d valid=%s'%(off,v, 1<=v<=row_count))
print('u16@+8=%d u16@+10=%d'%(u16(p,cp+8),u16(p,cp+10)))