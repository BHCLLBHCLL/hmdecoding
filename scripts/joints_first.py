import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
segs=D.find_elem_segments(p)
sh=[s[0] for s in segs if s[1]==1][0]
print('seg1 @',sh,'header:',[hex(u32(p,sh+k*4)) for k in range(6)])
# first CONST record
cp=None
for off in range(sh+16,sh+200,4):
    if is_const(u32(p,off)): cp=off; break
print('first CONST @',cp)
for off in range(0,48,4):
    print('  +%02d: %08x  u16[%d]=%d'%(off,u32(p,cp+off),off,u16(p,cp+off)))