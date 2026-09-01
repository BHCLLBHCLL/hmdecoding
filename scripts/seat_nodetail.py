import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,d64
base=1256; stride=52
print('last 3 records k=1618..1620:')
for k in (1618,1619,1620):
    rec=base+k*stride
    nid=u32(p,rec+8)
    x=d64(p,rec+12)
    print('  k=%d rec=%d nid=%d x=%.4f'%(k,rec,nid,x))