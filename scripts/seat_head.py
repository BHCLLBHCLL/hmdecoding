import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,d64
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
# check first 5 records
for k in range(0,5):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
    print('k=%d nid=%d x=%g y=%g z=%g'%(k,nid,x,y,z))