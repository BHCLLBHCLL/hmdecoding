import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
j=2917113
print('eid20995 @',j,'dump u32 (j-16..j+64):')
for off in range(j-16,j+64,4):
    print('  %s%d: %08x'%('+' if off>=j else '',off-j,u32(p,off)))