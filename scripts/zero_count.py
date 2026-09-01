import sys,os,gzip
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
for fn,label,exp in [('C:/Program Files/Altair/2019/tutorials/hm/truck.hm','truck',212138),('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm','seat_2',1620),('C:/Program Files/Altair/2019/tutorials/hm/car_section.hm','car_section',26695),('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_start.hm','seat_start',1620)]:
    raw=open(fn,'rb').read()
    p=gzip.decompress(raw[0x0c:])
    ns=D.find_node_section(p)
    hi,count,base,stride,idoff,chain=ns
    zero=0; total=0
    for k in range(count):
        rec=base+k*stride
        if rec+stride>len(p): break
        nid=u32(p,rec+idoff)
        x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
        if not (1<=nid<=10000000 and abs(x)<1e9 and abs(y)<1e9 and abs(z)<1e9): break
        total+=1
        if x==0 and y==0 and z==0: zero+=1
    print('%s total=%d zero_coord=%d exp=%d skip0=%d'%(label,total,zero,exp,total-zero))