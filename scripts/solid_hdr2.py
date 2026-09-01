import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,u16,d64
# find all [0x88] headers and their count, and which base each implies
hits=[]
i=0
while True:
    i=p.find(b'\x88\x00\x00\x00',i,min(len(p),8000000))
    if i<0: break
    n=u32(p,i+4)
    if 1<=n<=10000000:
        hits.append((i,n))
    i+=1
hits.sort(key=lambda h:-h[1])
print('solid_map [0x88] headers (top 8):')
for hi,count in hits[:8]:
    print('  @%d count=%d'%(hi,count))
    # for each, what base would find_node_section test (hi-32..hi+48)
    for base in range(hi-32,hi+48,4):
        if base<0: continue
        nid=u32(p,base+8)
        x=d64(p,base+12)
        if 1<=nid<=10000000 and abs(x)<1e9:
            print('     base=%d nid=%d'%(base,nid))