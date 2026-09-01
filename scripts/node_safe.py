import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
def safe(x,y,z):
    return max(abs(x),abs(y),abs(z)) > 1e-5
for fn,label,exp in [('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm','seat_2',1620),('C:/Program Files/Altair/2019/tutorials/hm/truck.hm','truck',212138),('C:/Program Files/Altair/2019/tutorials/hm/car_section.hm','car_section',26695),('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_start.hm','seat_start',1620)]:
    raw=open(fn,'rb').read()
    p=gzip.decompress(raw[0x0c:])
    ns=D.find_node_section(p)
    hi,count,base,stride,idoff,chain=ns
    ok_all=0; ok_safe=0
    for k in range(count):
        rec=base+k*stride
        if rec+stride>len(p): break
        nid=u32(p,rec+idoff)
        x=d64(p,rec+12); y=d64(p,rec+20); z=d64(p,rec+28)
        if 1<=nid<=10000000 and abs(x)<1e9 and abs(y)<1e9 and abs(z)<1e9:
            ok_all+=1
            if safe(x,y,z): ok_safe+=1
    print('%s count=%d all_valid=%d safe_valid=%d  exp=%d'%(label,count,ok_all,ok_safe,exp))