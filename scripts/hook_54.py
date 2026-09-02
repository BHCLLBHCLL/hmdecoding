import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
cp=731898
print('hook 0x7054 anchor (eid 393067) u16 stream:')
for off in range(0,72,2):
    print('  @+%d: u16=%d'%(off,u16(p,cp+off)))