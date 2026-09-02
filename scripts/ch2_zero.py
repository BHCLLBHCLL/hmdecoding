import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,u16,d64
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/ansys/chapter2_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
ns=D.find_node_section(p)
print('chapter2_2 ns:', ns)
hi,count,base,stride,idoff,chain=ns
zero=[]
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
    if x==0 and y==0 and z==0:
        zero.append((k,rec,nid))
print('zero-coord records:', len(zero), zero[:10])