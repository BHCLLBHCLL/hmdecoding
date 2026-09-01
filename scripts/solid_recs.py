import sys,os,gzip
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,d64
base=24527; stride=52; count=5
print('records:')
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+8)
    x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
    print('  k=%d rec=%d nid=%d x=%.4f y=%.4f z=%.4f'%(k,rec,nid,x,y,z))