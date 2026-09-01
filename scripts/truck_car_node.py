import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
for fn,label in [('C:/Program Files/Altair/2019/tutorials/hm/truck.hm','truck'),('C:/Program Files/Altair/2019/tutorials/hm/car_section.hm','car_section')]:
    raw=open(fn,'rb').read()
    p=gzip.decompress(raw[0x0c:])
    ns=D.find_node_section(p)
    hi,count,base,stride,idoff,chain=ns
    print('%s ns=%s'%(label,ns))
    # check last 3 records for coord anomalies
    for k in range(max(0,count-3),count):
        rec=base+k*stride
        nid=struct.unpack_from('<I',p,rec+idoff)[0] if False else u32(p,rec+idoff)
        x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
        print('  k=%d nid=%d x=%g y=%g z=%g'%(k,nid,x,y,z))