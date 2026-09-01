import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,u16,d64
ns=D.find_node_section(p)
print('solid_map find_node_section:', ns)
hi,count,base,stride,idoff,chain=ns
print('per record check:')
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    x=d64(p,rec+12)
    print('  k=%d rec=%d nid=%d x=%g'%(k,rec,nid,x))