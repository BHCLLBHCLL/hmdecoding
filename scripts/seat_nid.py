import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,d64
base=1256; stride=52; count=1621
nids=[]
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+8)
    x=d64(p,rec+12)
    nids.append(nid)
# find duplicates or non-monotonic
from collections import Counter
c=Counter(nids)
dups={k:v for k,v in c.items() if v>1}
print('duplicate nids:', dups)
print('total distinct:', len(set(nids)))
print('min,max:', min(nids), max(nids))
# find nids that break monotonicity or gaps
prev=0
gaps=[]
for i,nid in enumerate(nids):
    if nid!=prev+1 and i>0:
        gaps.append((i,nid,prev))
    prev=nid
print('non-contiguous (i,nid,prev):', gaps[:10], '... total', len(gaps))