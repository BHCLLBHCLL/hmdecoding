import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
sh=127516; cnt=4
s=None
for off in range(sh+16, min(sh+80, len(p)-4)):
    if is_const(u32(p,off)): s=off; break
print('anchor s=', s, 'const=', '%08x'%u32(p,s))
rec=s
const=u32(p,rec)
print('const>>16=', hex(const>>16))
e18=u16(p,rec+18); e4=u32(p,rec+4)
e = e18 if (0 < e18 < 10_000_000 and e18 != e4 and e4 < 100000) else e4
print('e18=%d e4=%d e=%d'%(e18,e4,e))
print('u16@+44=%d u16@+46=%d u16@+50=%d'%(u16(p,rec+44),u16(p,rec+46),u16(p,rec+50)))