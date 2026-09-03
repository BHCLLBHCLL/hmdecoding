import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
oracle=set(int(x.strip()) for x in open('output/ground_truth/sm_nodes_all.txt',encoding='utf-8') if x.strip().isdigit())
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
deleted=[]
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+44)-1
    if nid not in oracle:
        x,y,z=d64(p,rec),d64(p,rec+8),d64(p,rec+16)
        deleted.append((k,nid,x,y,z))
print('deleted nodes:',len(deleted))
for d in deleted[:8]:
    print('  k=%d nid=%d x=%g y=%g z=%g'%d)