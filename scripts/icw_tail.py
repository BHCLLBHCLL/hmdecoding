import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/icw_ex1.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,d64
base=20088; stride=56; count=89
print('tail records k=74..88:')
for k in range(74,count):
    rec=base+k*stride
    print('  k=%d  rec=%d  raw@+44=0x%08x  nid=%d  x=%.4f y=%.4f z=%.4f'%(k,rec,u32(p,rec+44),u32(p,rec+44)-1,d64(p,rec),d64(p,rec+8),d64(p,rec+16)))