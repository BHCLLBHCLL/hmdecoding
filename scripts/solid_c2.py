import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,u16,d64
# header @332893 count=2; find best base (2 consecutive valid 52B records)
hi=332893; count=2
print('testing bases near header @%d (count=2):'%hi)
for base in range(hi-32,hi+48,4):
    if base<0: continue
    ok=0; ids=[]
    for k in range(count):
        rec=base+k*52
        if rec+52>len(p): break
        nid=u32(p,rec+8)
        x=d64(p,rec+12)
        if 1<=nid<=10000000 and abs(x)<1e9:
            ok+=1; ids.append(nid)
    if ok>=2:
        print('  base=%d ok=%d ids=%s'%(base,ok,ids))
print('--- found records at base=332896/332897: ---')
for k in range(4):
    rec=332896+k*52
    if rec+52>len(p): continue
    nid=u32(p,rec+8)
    x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
    print('  k=%d rec=%d nid=%d x=%g y=%g z=%g'%(k,rec,nid,x,y,z))