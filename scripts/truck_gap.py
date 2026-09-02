import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,u16,d64
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
# nid sequence around k=209424 (residual 2220530); check gap: 2220530 -> 2220539 (missing 531..538)
for kk in range(209418,209434):
    rec=base+kk*stride
    nid=u32(p,rec+idoff)
    print('k=%d nid=%d'%(kk,nid))