import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
print('chain raw nid (no backfill), breaks:')
prev=0; breaks=[]
for k in range(count):
    rec=base+k*stride
    raw=u32(p,rec+44)
    nid=raw-1
    if not (1<=nid<=10000000):
        breaks.append((k,raw,nid,prev))
    else:
        prev=nid
print('breaks (k, raw, nid, prev_nid):')
for b in breaks[:20]: print('  ',b)
print('total breaks',len(breaks))