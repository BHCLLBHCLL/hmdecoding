import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,u16,d64
def safe_coord(x,y,z):
    return max(abs(x),abs(y),abs(z)) > 1e-5
for fn,label in [('C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm','solid_map'),('C:/Program Files/Altair/2019/tutorials/hm/truck.hm','truck')]:
    raw=open(fn,'rb').read()
    p=gzip.decompress(raw[0x0c:])
    ns=D.find_node_section(p)
    print('%s find_node_section=%s'%(label,ns))
    hi,count,base,stride,idoff,chain=ns
    # re-score with safe_coord: count valid records with max(|xyz|)>1e-5
    ok=0
    for k in range(min(count,60)):
        rec=base+k*stride
        if rec+stride>len(p): break
        nid=u32(p,rec+idoff)
        x=d64(p,rec+12); y=d64(p,rec+20); z=d64(p,rec+28)
        if 1<=nid<=10000000 and safe_coord(x,y,z): ok+=1
    print('   safe_coord valid=%d (of count=%d)'%(ok,count))