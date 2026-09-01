import sys,os,gzip
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
# truck: find zero-coord/non-model residual nodes (all id present in node table but deleted)
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
# truck extra residual = the zero coord record
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
    if x==0 and y==0 and z==0:
        print('truck zero-coord residual k=%d nid=%d'%(k,nid))