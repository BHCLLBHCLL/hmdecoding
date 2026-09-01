import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
bad=[]
for k in range(count):
    rec=base+k*stride
    if rec+stride>len(p): break
    nid=u32(p,rec+idoff)
    x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
    if 1<=nid<=10000000 and not (max(abs(x),abs(y),abs(z)) > 1e-5):
        bad.append((k,rec,nid,x,y,z))
print('truck safe_coord-bad records:', len(bad))
for b in bad[:10]:
    print('  k=%d rec=%d nid=%d x=%g y=%g z=%g'%b)