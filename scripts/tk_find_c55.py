import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# find CONST records where @+18 (family) or storage id yields eid 219946
eid=219946
for i in range(len(p)-200):
    if is_const(u32(p,i)):
        # family-1: eid=(u16@+18)|(u16@+20<<16) or @+4
        f1=(u16(p,i+18)|(u16(p,i+20)<<16))
        if f1==eid or u32(p,i+4)==eid or u32(p,i+20)==eid or u32(p,i+8)==eid:
            print('CONST @',i,'const=%08x f1=%d @+4=%d @+8=%d'%(u32(p,i),f1,u32(p,i+4),u32(p,i+8)))