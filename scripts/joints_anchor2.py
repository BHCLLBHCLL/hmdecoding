import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
cp=127552
print('seg11 rec0 (0x7050 anchor eid6072) dump:')
for off in range(0,120,4):
    print('  @+%03d: %08x  u16=%d'%(off,u32(p,cp+off),u16(p,cp+off)))