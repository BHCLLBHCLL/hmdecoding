import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
sh=65832
print('seg1 header @',sh,'u32:',[hex(u32(p,sh+k*4)) for k in range(6)])
print('sh+24..+100:')
for off in range(24,100,4):
    print('  +%02d: %08x  u16[%d]=%d u16[%d]=%d'%(off,u32(p,sh+off),off,u16(p,sh+off),off+2,u16(p,sh+off+2)))