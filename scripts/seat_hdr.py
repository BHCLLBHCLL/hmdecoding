import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,u16,d64
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
hi=1252
print('node header @%d:'%hi)
for off in range(0,40,4):
    print('  @%d %08x'%(hi+off,u32(p,hi+off)))
rec=1256+148*52
print('nid149 record rec=%d:'%rec)
for off in range(0,60,4):
    print('  @%d %08x'%(rec+off,u32(p,rec+off)))