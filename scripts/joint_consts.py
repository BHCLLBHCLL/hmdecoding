import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# find all CONST in segid11 region 127516..128196
recs=[]; pos=127516+16; end=128196
while pos<end:
    if is_const(u32(p,pos)): recs.append(pos)
    pos+=4
print('consts:', recs)
for cp in recs:
    print(' @%d const=%08x u16[+22]=%d u32[+4]=%d u16[+18]=%d'%(cp,u32(p,cp),u16(p,cp+22),u32(p,cp+4),u16(p,cp+18)))