import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,d64
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
recs=[]
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
    recs.append((nid,round(x,3),round(y,3),round(z,3)))
zero=[r for r in recs if r[1]==0 and r[2]==0 and r[3]==0]
print('zero-coord records:', len(zero), zero[:5])
from collections import Counter
cc=Counter((x,y,z) for _,x,y,z in recs)
dups=[k for k,v in cc.items() if v>1]
print('dup coords:', dups[:5], 'count', len(dups))