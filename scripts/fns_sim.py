import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
NODE_LAYOUTS = D.NODE_LAYOUTS
def safe(x,y,z):
    return max(abs(x),abs(y),abs(z)) > 1e-5
def find_best(p):
    # replica of find_node_section but with safe-coord criterion
    hits=[]
    i=0
    while True:
        i=p.find(b'\x88\x00\x00\x00',i,min(len(p),8000000))
        if i<0: break
        n=D.u32(p,i+4)
        if 1<=n<=10000000: hits.append((i,n))
        i+=1
    hits.sort(key=lambda h:-h[1])
    best=None
    for hi,count in hits[:600]:
        for base in range(hi-32,hi+48,4):
            if base<0: continue
            for stride,idoff,xoff,chain in NODE_LAYOUTS:
                ok=0; bad=0; seen=set()
                for k in range(min(count,60)):
                    rec=base+k*stride
                    if rec+stride>len(p): break
                    if chain:
                        tailok=D.u32(p,rec+48)==0 and D.u32(p,rec+52)==0
                        nid=D.u32(p,rec+44)-1
                    else:
                        tailok=True
                        nid=D.u32(p,rec+idoff)
                    x=d64(p,rec+xoff); y=d64(p,rec+xoff+8); z=d64(p,rec+xoff+16)
                    if 1<=nid<=10000000 and abs(x)<1e9 and abs(y)<1e9 and abs(z)<1e9 and safe(x,y,z) and tailok:
                        ok+=1; seen.add(nid)
                    else:
                        bad+=1
                        if bad>3: break
                if len(seen)<max(2,ok//2): continue
                need=max(1,min(count,max(3,int(min(count,60)*0.8))))
                if ok>=need and (best is None or ok>best[0]):
                    best=(ok,(hi,count,base,stride,idoff,chain))
    return best[1] if best and best[0]>=max(1,min(best[1][1],max(3,int(min(best[1][1],60)*0.8)))) else None
for fn,label in [('C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm','solid_map'),('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm','seat_2'),('C:/Program Files/Altair/2019/tutorials/hm/truck.hm','truck'),('C:/Program Files/Altair/2019/tutorials/hm/car_section.hm','car_section'),('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_start.hm','seat_start')]:
    raw=open(fn,'rb').read()
    p=gzip.decompress(raw[0x0c:])
    print('%s  ORIG=%s  NEW=%s'%(label, D.find_node_section(p), find_best(p)))