import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
print('chain nodes: base=%d count=%d stride=%d'%(base,count,stride))
prev=0; breaks=[]
for k in range(count):
    rec=base+k*stride
    if rec+stride>len(p): break
    nid=u32(p,rec+44)-1
    if not (1<=nid<=10000000):
        breaks.append((k,nid,prev))
    prev=max(prev,nid if 1<=nid<=10000000 else 0)
print('break points (k, nid, prev):', breaks[:20], 'total', len(breaks))