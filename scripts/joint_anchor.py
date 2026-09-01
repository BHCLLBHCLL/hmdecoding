import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# inspect 0x70501ff5 anchor @127552 (eid 6072) - is it a real element?
cp=127552
print('anchor @',cp, 'const=%08x'%u32(p,cp))
for off in range(0,64,4):
    v=u32(p,cp+off)
    print('  +%02d: %08x'%(off,v))