import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
cp=127676
print('seg11 rec1 (eid 6073) u32 dump:')
for off in range(0,108,4):
    print('  @+%03d: %08x  u16[+%d]=%d'%(off,u32(p,cp+off),off,u16(p,cp+off)))